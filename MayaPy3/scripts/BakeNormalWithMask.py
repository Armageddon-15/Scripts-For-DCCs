"""BakeNormalWithMask.py

用法:
    1. 在 Maya 视口中先选目标 mesh A (可多个, 支持 transform/shape/face 组件)
       - 同一个 mesh 的多组 face/vtx 选择会自动合并, 整 mesh 只处理一次
    2. 最后一个选中法线来源 mesh B
    3. 执行: import BakeNormalWithMask; BakeNormalWithMask.bake_normal_with_mask()

可选参数 (在调用 bake_normal_with_mask 时传):
    kernel_radius: float or None
        在 B 上做核函数加权法线采样时的搜索半径(世界空间). None 表示自动取 B 的
        包围盒对角线 * 0.05.
    max_samples: int
        每个 A 顶点在半径内最多采样多少个 B 顶点 (类似 Houdini Attribute Transfer
        的 "Max Sample Count"). 默认 8.

流程:
    - 按 shape 合并 A 端的选择
    - 每个 A 复制一份为 C (保留 A->C 顶点 id 映射, 整 shape 时为 identity)
    - 在 C 上跑 transferAttributes 把 B 的法线传过去 (作为视觉/中间产物)
    - 用 Elendt-style 平滑径向核在 B 的顶点样本上做加权 (kernel_radius / max_samples)
      得到 c_normals; 比单点 getClosestNormal 更平滑, 也是 Houdini Attribute Transfer
      的 Elendt 核做的事
    - 读 A 的顶点色 R 通道作为遮罩, 在 world space 用 lerp(A_normal, C_normal, R)
      合成出每个顶点的世界法线
    - 逐 face-vertex 单独建 TBN (不在顶点级别累加 tangent, UV 接缝处的切线可以不同),
      把世界法线转到切线空间, *0.5 + 0.5 打包到 0~1
    - 用 setFaceVertexColors 写入 A 的 face-vertex 顶点色 (A=1), 不修改 A 的法线
    - 删除 C

依赖: maya.cmds + maya.api.OpenMaya (API 2.0)
"""

import math
import maya.cmds as cmds
import maya.api.OpenMaya as om


# -------------------------------------------------------------
# 基础工具
# -------------------------------------------------------------
def _get_dag(name):
    sl = om.MSelectionList()
    sl.add(name)
    return sl.getDagPath(0)


def _get_mesh_shape(node):
    """传入 transform / shape / 组件路径前缀, 返回 mesh shape 的 long name"""
    base = node.split(".")[0] if "." in node else node
    if cmds.objectType(base) == "mesh":
        return cmds.ls(base, long=True)[0]
    shapes = cmds.listRelatives(
        base, shapes=True, fullPath=True, type="mesh", noIntermediate=True
    ) or []
    if not shapes:
        raise RuntimeError(u"{0} 找不到 mesh shape".format(node))
    return shapes[0]


def _resolve_target(sel_item):
    """
    解析 A 的一个选择项, 返回 (shape_long_name, vert_id_filter_or_None).
    vert_id_filter 为 None 表示对全部顶点生效.
    """
    if "." in sel_item and "[" in sel_item:
        shape = _get_mesh_shape(sel_item)
        if ".vtx[" in sel_item:
            comps = cmds.ls(sel_item, flatten=True) or []
        elif ".f[" in sel_item:
            conv = cmds.polyListComponentConversion(
                sel_item, fromFace=True, toVertex=True
            ) or []
            comps = cmds.ls(conv, flatten=True) or []
        elif ".e[" in sel_item:
            conv = cmds.polyListComponentConversion(
                sel_item, fromEdge=True, toVertex=True
            ) or []
            comps = cmds.ls(conv, flatten=True) or []
        else:
            return shape, None
        vert_ids = sorted({int(c.split("[")[-1].rstrip("]")) for c in comps})
        return shape, vert_ids
    return _get_mesh_shape(sel_item), None


# -------------------------------------------------------------
# 几何 / 法线 / 切线工具
# -------------------------------------------------------------
def _get_vertex_normals_world(mesh_fn, mesh_dag):
    """
    返回每个顶点的平均法线 (世界空间, list[MVector]).
    使用 raw normals + MItMeshVertex.getNormalIndices() 而不是 getVertexNormal,
    这样能正确读到 transferAttributes 之类设置的 user-locked normals.
    """
    n_verts = mesh_fn.numVertices
    raw = mesh_fn.getNormals(om.MSpace.kWorld)  # MFloatVectorArray, 按 normalId 索引
    out = [om.MVector(0.0, 0.0, 0.0) for _ in range(n_verts)]

    it = om.MItMeshVertex(mesh_dag)
    while not it.isDone():
        vid = it.index()
        try:
            nids = it.getNormalIndices()
        except Exception:
            nids = []
        avg = om.MVector(0.0, 0.0, 0.0)
        cnt = 0
        for nid in nids:
            if 0 <= nid < len(raw):
                avg += om.MVector(raw[nid])
                cnt += 1
        if cnt > 0:
            avg = avg / float(cnt)
        if avg.length() > 1e-8:
            avg.normalize()
        out[vid] = avg
        it.next()
    return out


def _make_tbn(T_raw, N_raw):
    """
    给定一组原始 T / N (任意方向, 不一定单位、不一定正交),
    返回 (T, B, N) 单位正交基, B = N x T.
    退化时给一个合理的备用 T.
    """
    N = om.MVector(N_raw)
    if N.length() < 1e-8:
        N = om.MVector(0.0, 1.0, 0.0)
    N.normalize()

    T = om.MVector(T_raw)
    # 把 T 投影到 N 的正交补空间
    T = T - N * (T * N)
    if T.length() < 1e-8:
        ref = om.MVector(1.0, 0.0, 0.0) if abs(N.x) < 0.9 else om.MVector(0.0, 1.0, 0.0)
        T = ref ^ N
        if T.length() < 1e-8:
            T = om.MVector(1.0, 0.0, 0.0)
    T.normalize()
    B = N ^ T
    B *= -1
    if B.length() > 1e-8:
        B.normalize()
    return T, B, N


def _get_vertex_r_mask(mesh_fn):
    """
    读 A 当前 color set 的 R 通道, 返回 list[float] (长度 = numVertices).
    没有顶点色 / 没读到 -> 全 0.
    """
    n_verts = mesh_fn.numVertices
    mask = [0.0] * n_verts
    try:
        css = mesh_fn.getColorSetNames()
    except Exception:
        css = []
    if not css:
        return mask
    try:
        cs = mesh_fn.currentColorSetName()
        if cs not in css:
            cs = css[0]
    except Exception:
        cs = css[0]
    try:
        colors = mesh_fn.getVertexColors(cs)
        for vid in range(min(n_verts, len(colors))):
            r = colors[vid].r
            if r < 0.0:
                r = 0.0
            elif r > 1.0:
                r = 1.0
            mask[vid] = r
    except Exception:
        pass
    return mask


# -------------------------------------------------------------
# Elendt-style 核加权法线传递
# -------------------------------------------------------------
def _elendt_weight(r):
    """
    r 是归一化距离 d / kernel_radius, [0, 1] 外返回 0.
    Wendland-style 平滑核: (1 - r^2)^3 * (1 + 3 r^2)
    在 r=0 时为 1, 在 r=1 时及一阶导都为 0, C^1 连续 (Houdini 的 Elendt 核也是这一族).
    """
    if r >= 1.0 or r < 0.0:
        return 0.0
    r2 = r * r
    return (1.0 - r2) ** 3 * (1.0 + 3.0 * r2)


class _Grid3D(object):
    """
    简易 3D 均匀网格 hash, cell_size = kernel_radius, 用于 fixed-radius KNN.
    建表 O(N), 单次查询期望只看 27 个 cell.
    """

    def __init__(self, positions, cell_size):
        self.cell_size = max(float(cell_size), 1e-6)
        self.positions = positions
        self.cells = {}
        cs = self.cell_size
        for idx, p in enumerate(positions):
            key = (int(math.floor(p[0] / cs)),
                   int(math.floor(p[1] / cs)),
                   int(math.floor(p[2] / cs)))
            bucket = self.cells.get(key)
            if bucket is None:
                self.cells[key] = [idx]
            else:
                bucket.append(idx)

    def query_within_radius(self, p, radius):
        """返回 [(idx, sq_distance), ...], 距离 <= radius 的所有样本."""
        cs = self.cell_size
        rs = int(math.ceil(radius / cs))
        kx = int(math.floor(p[0] / cs))
        ky = int(math.floor(p[1] / cs))
        kz = int(math.floor(p[2] / cs))
        r2 = radius * radius
        out = []
        positions = self.positions
        cells = self.cells
        px, py, pz = p[0], p[1], p[2]
        for dx in range(-rs, rs + 1):
            kx2 = kx + dx
            for dy in range(-rs, rs + 1):
                ky2 = ky + dy
                for dz in range(-rs, rs + 1):
                    bucket = cells.get((kx2, ky2, kz + dz))
                    if not bucket:
                        continue
                    for idx in bucket:
                        q = positions[idx]
                        d2 = (q[0] - px) ** 2 + (q[1] - py) ** 2 + (q[2] - pz) ** 2
                        if d2 <= r2:
                            out.append((idx, d2))
        return out


def _build_source_samples(source_shape):
    """
    把 B 的所有顶点作为采样点, 返回 (positions, normals):
      positions: list[tuple(x,y,z)]   世界空间坐标
      normals:   list[MVector]        世界空间法线 (单位向量)
    """
    src_dag = _get_dag(source_shape)
    src_fn = om.MFnMesh(src_dag)
    n_verts = src_fn.numVertices

    raw_normals = src_fn.getNormals(om.MSpace.kWorld)
    normals = [om.MVector(0.0, 0.0, 0.0) for _ in range(n_verts)]
    it = om.MItMeshVertex(src_dag)
    while not it.isDone():
        vid = it.index()
        try:
            nids = it.getNormalIndices()
        except Exception:
            nids = []
        avg = om.MVector(0.0, 0.0, 0.0)
        cnt = 0
        for nid in nids:
            if 0 <= nid < len(raw_normals):
                avg += om.MVector(raw_normals[nid])
                cnt += 1
        if cnt > 0:
            avg = avg / float(cnt)
        if avg.length() > 1e-8:
            avg.normalize()
        normals[vid] = avg
        it.next()

    pts = src_fn.getPoints(om.MSpace.kWorld)  # MPointArray
    positions = [(pts[i].x, pts[i].y, pts[i].z) for i in range(len(pts))]
    return positions, normals


def _auto_kernel_radius(source_shape):
    """B 包围盒对角 * 0.05, 作为默认 kernel_radius."""
    bb = cmds.exactWorldBoundingBox(source_shape)  # [xmin,ymin,zmin,xmax,ymax,zmax]
    dx = bb[3] - bb[0]
    dy = bb[4] - bb[1]
    dz = bb[5] - bb[2]
    diag = math.sqrt(dx * dx + dy * dy + dz * dz)
    return max(diag * 0.05, 1e-4)


def _sample_normal_elendt(a_pt, grid, src_positions, src_normals,
                          kernel_radius, max_samples, fallback_fn=None):
    """
    在 source 样本上做 Elendt 加权采样, 返回世界空间法线 (MVector, 单位向量).
    若半径内无样本, 用 fallback_fn(MPoint) 兜底 (通常是 getClosestNormal).
    """
    p = (a_pt.x, a_pt.y, a_pt.z)
    neighbors = grid.query_within_radius(p, kernel_radius)
    if not neighbors:
        if fallback_fn is not None:
            try:
                n_vec, _fid = fallback_fn(om.MPoint(a_pt), om.MSpace.kWorld)
                n = om.MVector(n_vec)
                if n.length() > 1e-8:
                    n.normalize()
                return n
            except Exception:
                pass
        return om.MVector(0.0, 1.0, 0.0)

    if len(neighbors) > max_samples:
        neighbors.sort(key=lambda x: x[1])
        neighbors = neighbors[:max_samples]

    inv_r = 1.0 / kernel_radius
    acc = om.MVector(0.0, 0.0, 0.0)
    total_w = 0.0
    for idx, d2 in neighbors:
        d = math.sqrt(d2)
        w = _elendt_weight(d * inv_r)
        if w <= 0.0:
            continue
        acc += src_normals[idx] * w
        total_w += w

    if total_w <= 1e-12:
        # 半径内的点权重都 0 (距离恰好 = R), 兜底
        if fallback_fn is not None:
            try:
                n_vec, _fid = fallback_fn(om.MPoint(a_pt), om.MSpace.kWorld)
                n = om.MVector(n_vec)
                if n.length() > 1e-8:
                    n.normalize()
                return n
            except Exception:
                pass
        return om.MVector(0.0, 1.0, 0.0)

    acc = acc / total_w
    if acc.length() > 1e-8:
        acc.normalize()
    return acc


def _ensure_color_set(mesh_fn, target_xform):
    """确保 mesh 有可用的当前 color set, 并把 displayColors 打开."""
    css = mesh_fn.getColorSetNames()
    if css:
        cs_name = mesh_fn.currentColorSetName()
        if cs_name not in css:
            cs_name = css[0]
            mesh_fn.setCurrentColorSetName(cs_name)
    else:
        cs_name = mesh_fn.createColorSetWithName("colorSet1")
        mesh_fn.setCurrentColorSetName(cs_name)
    try:
        if not cmds.getAttr(target_xform + ".displayColors"):
            cmds.setAttr(target_xform + ".displayColors", 1)
    except Exception:
        pass


def _write_face_vertex_colors(mesh_fn, target_xform, fv_colors, fv_faces, fv_verts):
    """按 (face_id, vertex_id) 写 face-vertex 顶点色, 不影响其他 face-vertex."""
    _ensure_color_set(mesh_fn, target_xform)
    mesh_fn.setFaceVertexColors(fv_colors, fv_faces, fv_verts)


# -------------------------------------------------------------
# 核心流程
# -------------------------------------------------------------
def _group_targets_by_shape(target_sels):
    """
    把 A 端的多个选择项按 shape 合并.
    返回 [(shape_long, vert_filter_or_None), ...], 同一 shape 只出现一次.
    - 任一选择项为整 shape (无组件) -> 该 shape 的 filter 为 None (全部顶点)
    - 否则取所有组件涉及顶点的并集
    """
    grouped = {}            # shape_long -> set(vert_id) 或 None (表示全选)
    order = []              # 保留首次出现顺序
    for sel in target_sels:
        shape, vids = _resolve_target(sel)
        if shape not in grouped:
            order.append(shape)
            grouped[shape] = set() if vids is not None else None
            if vids is not None:
                grouped[shape].update(vids)
        else:
            # 已经是 None (整 shape) -> 保持 None
            if grouped[shape] is None:
                continue
            # 新增项是整 shape -> 升级为 None
            if vids is None:
                grouped[shape] = None
            else:
                grouped[shape].update(vids)

    result = []
    for shape in order:
        s = grouped[shape]
        result.append((shape, None if s is None else sorted(s)))
    return result


def _bake_one(target_shape, vert_filter, source_shape,
              source_grid=None, source_positions=None, source_normals=None,
              kernel_radius=None, max_samples=8):
    target_dag = _get_dag(target_shape)
    target_fn = om.MFnMesh(target_dag)
    target_xform = cmds.listRelatives(target_shape, parent=True, fullPath=True)[0]
    short = target_xform.split("|")[-1]

    n_verts = target_fn.numVertices

    # ---------- 1) 复制 A 为 C (留给视觉验证 + 之后可能用到的 vid 映射) ----------
    dup = cmds.duplicate(target_xform, name=short + "_BNWM_C")[0]
    for ch in cmds.listRelatives(dup, children=True, fullPath=True) or []:
        if cmds.objectType(ch) != "mesh":
            try:
                cmds.delete(ch)
            except Exception:
                pass
    dup_shapes = cmds.listRelatives(
        dup, shapes=True, fullPath=True, type="mesh", noIntermediate=True
    ) or []
    if not dup_shapes:
        cmds.delete(dup)
        raise RuntimeError(u"复制 {0} 失败".format(short))
    dup_shape = dup_shapes[0]

    # 记录顶点 id 映射 (A_vid -> C_vid). 全复制是 identity.
    vid_map_a_to_c = {i: i for i in range(n_verts)}

    # ---------- 2) 读 A 原本法线 ----------
    a_normals = _get_vertex_normals_world(target_fn, target_dag)

    # ---------- 3) (可选) transferAttributes 把 B 的法线传给 C, 仅供视觉验证 ---------
    try:
        cmds.transferAttributes(
            source_shape, dup_shape,
            transferPositions=0,
            transferNormals=1,
            transferUVs=0,
            transferColors=0,
            sampleSpace=0,
            searchMethod=3,
        )
    except Exception as e:
        cmds.warning(u"[BakeNormalWithMask] transferAttributes 失败(仅视觉影响): {0}".format(e))

    # ---------- 4) 用 Elendt 核在 B 的顶点样本上做加权法线采样 ----------
    src_dag = _get_dag(source_shape)
    src_fn = om.MFnMesh(src_dag)
    c_normals = [None] * n_verts
    for vid in range(n_verts):
        a_pt = target_fn.getPoint(vid, om.MSpace.kWorld)
        try:
            n = _sample_normal_elendt(
                a_pt, source_grid, source_positions, source_normals,
                kernel_radius, max_samples,
                fallback_fn=src_fn.getClosestNormal,
            )
        except Exception:
            n = om.MVector(a_normals[vid])
        c_normals[vid] = n

    # ---------- 5) 读 A 的 R 通道作为遮罩, 在 world space 用 R 线性混合 ----------
    r_mask = _get_vertex_r_mask(target_fn)
    if sum(1 for r in r_mask if r > 1e-4) == 0:
        cmds.warning(u"[BakeNormalWithMask] {0} 的顶点色 R 通道全为 0, 混合后法线和原模型完全一样, "
                     u"请检查目标 mesh 的 current color set".format(short))

    final_world_normals = [None] * n_verts
    flt = None if vert_filter is None else set(vert_filter)
    for vid in range(n_verts):
        a_n = a_normals[vid]
        if flt is not None and vid not in flt:
            final_world_normals[vid] = a_n
            continue
        c_vid = vid_map_a_to_c.get(vid, vid)
        c_n = c_normals[c_vid] if 0 <= c_vid < len(c_normals) else a_n
        r = r_mask[vid]
        if r <= 0.0:
            n = om.MVector(a_n)
        elif r >= 1.0:
            n = om.MVector(c_n)
        else:
            n = a_n * (1.0 - r) + c_n * r
        if n.length() > 1e-8:
            n.normalize()
        final_world_normals[vid] = n

    # ---------- 6) 逐 face-vertex 计算自己的 TBN, 把世界法线转到切线空间, 打包到 0~1 ----------
    #   不再按顶点平均 tangent, UV 接缝处不同 face-vertex 的切线可以不同.
    fv_faces = om.MIntArray()
    fv_verts = om.MIntArray()
    fv_colors = om.MColorArray()

    has_uv = False
    try:
        has_uv = target_fn.numUVs() > 0
    except Exception:
        has_uv = False
    if not has_uv:
        cmds.warning(u"[BakeNormalWithMask] {0} 没有 UV, 切线空间无定义, 结果可能不可用".format(short))

    it = om.MItMeshFaceVertex(target_dag)
    while not it.isDone():
        vid = it.vertexId()
        if flt is None or vid in flt:
            fid = it.faceId()
            try:
                T_raw = om.MVector(it.getTangent(om.MSpace.kWorld))
            except Exception:
                T_raw = om.MVector(1.0, 0.0, 0.0)
            try:
                N_raw = om.MVector(it.getNormal(om.MSpace.kWorld))
            except Exception:
                N_raw = om.MVector(final_world_normals[vid])

            T, B, N = _make_tbn(T_raw, N_raw)

            n_w = final_world_normals[vid]
            # 世界 -> 切线: TBN 正交基, 转置即逆, 取 n 在 T/B/N 上的投影
            nt = om.MVector(T * n_w, B * n_w, N * n_w)
            if nt.length() > 1e-8:
                nt.normalize()
            r = nt.x * 0.5 + 0.5
            g = nt.y * 0.5 + 0.5
            b = nt.z * 0.5 + 0.5

            fv_faces.append(fid)
            fv_verts.append(vid)
            fv_colors.append(om.MColor((r, g, b, 1.0)))
        it.next()

    # ---------- 7) 写入 A 的 face-vertex 顶点色 (不修改 A 的法线) ----------
    _write_face_vertex_colors(target_fn, target_xform, fv_colors, fv_faces, fv_verts)

    # ---------- 8) 删除 C ----------
    try:
        cmds.delete(dup)
    except Exception:
        pass


def bake_normal_with_mask(kernel_radius=None, max_samples=8):
    """主入口: 处理当前选择

    Args:
        kernel_radius (float | None): Elendt 核的搜索半径 (世界空间). None 时使用
            B 的包围盒对角线 * 0.05 作为默认值.
        max_samples (int): 每个 A 顶点在半径内最多采样多少个 B 顶点, 类似 Houdini
            Attribute Transfer 的 Max Sample Count. 默认 8.
    """
    sel = cmds.ls(selection=True, long=True) or []
    if len(sel) < 2:
        cmds.warning(u"请至少选择 2 个: 前面为目标 A (可多个, 支持 face/vtx 组件), 最后一个为法线来源 B")
        return

    targets = sel[:-1]
    source = sel[-1]

    try:
        source_shape = _get_mesh_shape(source)
    except Exception as e:
        cmds.error(u"法线来源 B 无法解析为 mesh: {0}".format(e))
        return

    grouped = _group_targets_by_shape(targets)
    if not grouped:
        cmds.warning(u"未解析到任何有效的 A mesh")
        return

    if kernel_radius is None or kernel_radius <= 0.0:
        kernel_radius = _auto_kernel_radius(source_shape)
        print(u"[BakeNormalWithMask] 自动 kernel_radius = {0:.6f}".format(kernel_radius))
    if max_samples is None or max_samples < 1:
        max_samples = 8

    print(u"[BakeNormalWithMask] 构建 source 采样点 / 空间索引 ...")
    src_positions, src_normals = _build_source_samples(source_shape)
    grid = _Grid3D(src_positions, cell_size=kernel_radius)
    print(u"[BakeNormalWithMask] 共 {0} 个 source 样本, cell_size={1:.4f}".format(
        len(src_positions), kernel_radius))

    ok, fail = 0, 0
    for shape, vert_filter in grouped:
        try:
            _bake_one(
                shape, vert_filter, source_shape,
                source_grid=grid,
                source_positions=src_positions,
                source_normals=src_normals,
                kernel_radius=kernel_radius,
                max_samples=max_samples,
            )
            ok += 1
            n_info = u"全部" if vert_filter is None else u"{0} 个顶点".format(len(vert_filter))
            print(u"[BakeNormalWithMask] 完成: {0}  ({1})".format(shape, n_info))
        except Exception as e:
            fail += 1
            cmds.warning(u"[BakeNormalWithMask] 处理失败 {0}: {1}".format(shape, e))

    try:
        cmds.select(sel, replace=True)
    except Exception:
        pass

    print(u"[BakeNormalWithMask] 总计 {0} 成功, {1} 失败".format(ok, fail))


if __name__ == "__main__":
    bake_normal_with_mask(kernel_radius=2.0, max_samples=2)
