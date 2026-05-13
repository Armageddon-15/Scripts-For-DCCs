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
    - 读 A 原本的世界法线
    - 用 Elendt-style 平滑径向核在 B 的顶点样本上做加权 (kernel_radius / max_samples)
      得到每个 A 顶点对应的 "从 B 取来" 的世界法线 c_normals
      (类似 Houdini Attribute Transfer 的 Elendt 核)
    - 读 A 的顶点色 R 通道作为遮罩, 在 world space 用 lerp(A_normal, C_normal, R)
      合成出每个顶点的世界法线 final_world_normals
    - 逐 face-vertex 用 MFnMesh.getFaceVertexTangent (MikkT) 拿到 per-face tangent
      和该 face-vertex 的法线, 建 TBN, 把 final_world_normals 转到切线空间
    - 用 octahedral encoding 把切线空间法线打包成 (u, v) ∈ [0,1]^2
    - 用 setUVs + assignUVs 写入 A 的一个新 UV set (ENCODED_NORMAL_UV_SET),
      identity uvIds 保证每个 face-vertex 独立一个 UV slot; A 的法线 / 顶点色都不动

依赖: maya.cmds + maya.api.OpenMaya (API 2.0)
"""

import math
import maya.cmds as cmds
import maya.api.OpenMaya as om


# 全局调试开关:
#   False - 正常流程: 切线空间转换 -> octahedral encode -> 写入 A 的新 UV set
#   True  - 调试模式: 跳过切线/UV, 直接把混合后的世界法线 setVertexNormals 写到 A 上,
#           便于在视口直接看法线混合是否正确
DEBUG = False

# 输出 UV set 名字; 已存在则复用同名 UV set
ENCODED_NORMAL_UV_SET = "normalEncoded"

def maya_useNewAPI():
    """
    Tell Maya use open maya 2
    """
    pass

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
    解析 A 的一个选择项, 返回 (shape_long_name, face_ids_or_None, vert_ids_or_None).
        - face 组件:   (shape, {face ids}, None)
        - vtx 组件:    (shape, None, {vert ids})
        - edge 组件:   (shape, None, {端点 vert ids})
        - 整 shape:    (shape, None, None)
    None 表示这一维度不约束 (整 shape 时两个都是 None).
    """
    if "." in sel_item and "[" in sel_item:
        shape = _get_mesh_shape(sel_item)
        if ".f[" in sel_item:
            comps = cmds.ls(sel_item, flatten=True) or []
            face_ids = {int(c.split("[")[-1].rstrip("]")) for c in comps}
            return shape, face_ids, None
        elif ".vtx[" in sel_item:
            comps = cmds.ls(sel_item, flatten=True) or []
            vert_ids = {int(c.split("[")[-1].rstrip("]")) for c in comps}
            return shape, None, vert_ids
        elif ".e[" in sel_item:
            conv = cmds.polyListComponentConversion(
                sel_item, fromEdge=True, toVertex=True
            ) or []
            comps = cmds.ls(conv, flatten=True) or []
            vert_ids = {int(c.split("[")[-1].rstrip("]")) for c in comps}
            return shape, None, vert_ids
        return shape, None, None
    return _get_mesh_shape(sel_item), None, None


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


def _octahedral_encode(n):
    """
    把一个单位 3D 向量映射到 [0, 1]^2 的 2D 点 (octahedral encoding).
    输入 n 可以是 MVector 或 (x, y, z) tuple. 假定已 normalize.

    encode 算法:
      1) 把 n 投影到八面体表面: p = n / (|x| + |y| + |z|)
      2) 上半球 (n.z >= 0) 直接用 (px, py)
      3) 下半球 (n.z <  0) 用 "对角折叠" 公式映射到外圈, 保持连续可解
      4) 把 [-1, 1] 重映射到 [0, 1]
    Shader 端需要用配套 decode 还原 (网上有很多版本).
    """
    if isinstance(n, om.MVector):
        nx, ny, nz = n.x, n.y, n.z
    else:
        nx, ny, nz = n[0], n[1], n[2]
    s = abs(nx) + abs(ny) + abs(nz)
    if s < 1e-8:
        return 0.5, 0.5
    inv = 1.0 / s
    px = nx * inv
    py = ny * inv
    if nz < 0.0:
        sign_x = 1.0 if px >= 0.0 else -1.0
        sign_y = 1.0 if py >= 0.0 else -1.0
        npx = (1.0 - abs(py)) * sign_x
        npy = (1.0 - abs(px)) * sign_y
        px, py = npx, npy
    return px * 0.5 + 0.5, py * 0.5 + 0.5


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
    # since we bake normal to unreal
    # it uses directx tangent space we need to invert bitangent
    # but uv.x in unreal is also invert compare to maya
    # so uv.x need to be invert
    # invert twice == no invert
    # B *= -1
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


def _ensure_uv_set(mesh_fn, uv_set_name):
    """如果 mesh 上没这个 UV set 就创建一个, 返回实际 UV set 名字."""
    sets = mesh_fn.getUVSetNames()
    if uv_set_name in sets:
        return uv_set_name
    try:
        return mesh_fn.createUVSetWithName(uv_set_name)
    except AttributeError:
        return mesh_fn.createUVSet(uv_set_name)


def _write_face_vertex_uvs(mesh_fn, uv_set_name, fv_uvs, default_uv=(0.5, 0.5)):
    """
    用 setUVs + assignUVs 写 face-vertex UV.
    每个 face-vertex 独占一个 UV slot, 共享同一全局 vertexId 的不同 face 也可有不同 UV.

    fv_uvs: list[(u, v) or None], 长度 = mesh 总 face-vertex 数, 按 MItMeshFaceVertex
        迭代顺序排列. None 表示该 face-vertex 用 default_uv (默认 (0.5, 0.5),
        对应 octahedral encode 的"切线空间 (0,0,1) = 未扰动" 的法线).
    """
    actual_name = _ensure_uv_set(mesh_fn, uv_set_name)

    n = len(fv_uvs)
    u_array = om.MFloatArray()
    v_array = om.MFloatArray()
    for uv in fv_uvs:
        if uv is None:
            u_array.append(default_uv[0])
            v_array.append(default_uv[1])
        else:
            u_array.append(uv[0])
            v_array.append(uv[1])

    # uvCounts: 每个面有几个 UV (等于面顶点数). uvIds: 每个 face-vertex 指向 UV pool 的索引,
    # identity 映射 -> 每个 face-vertex 独占一个 slot.
    n_polys = mesh_fn.numPolygons
    uv_counts = om.MIntArray()
    total = 0
    for fid in range(n_polys):
        c = mesh_fn.polygonVertexCount(fid)
        uv_counts.append(c)
        total += c
    if total != n:
        raise RuntimeError(
            "face-vertex 总数 ({0}) 与 fv_uvs 长度 ({1}) 不一致".format(total, n))

    uv_ids = om.MIntArray()
    for i in range(n):
        uv_ids.append(i)

    mesh_fn.setUVs(u_array, v_array, actual_name)
    mesh_fn.assignUVs(uv_counts, uv_ids, actual_name)


# -------------------------------------------------------------
# 核心流程
# -------------------------------------------------------------
def _group_targets_by_shape(target_sels):
    """
    把 A 端的多个选择项按 shape 合并.
    返回 [(shape_long, face_filter, vert_filter), ...], 同一 shape 只出现一次.
        - face_filter / vert_filter 各自可以是 set 或 None
        - 若任一选择项是 "整 shape" (face/vert 都是 None), 该 shape 升级为 (None, None)
          即不再做任何 filter
        - 其余情况按 face/vert 分别取并集
    """
    grouped = {}    # shape_long -> [face_set_or_None, vert_set_or_None, is_full]
    order = []
    for sel in target_sels:
        shape, faces, verts = _resolve_target(sel)
        is_full = faces is None and verts is None
        if shape not in grouped:
            order.append(shape)
            grouped[shape] = [None, None, False]
        entry = grouped[shape]
        if entry[2]:
            # 已经是整 shape, 后面的项不再有意义
            continue
        if is_full:
            entry[0] = None
            entry[1] = None
            entry[2] = True
            continue
        if faces is not None:
            if entry[0] is None:
                entry[0] = set(faces)
            else:
                entry[0].update(faces)
        if verts is not None:
            if entry[1] is None:
                entry[1] = set(verts)
            else:
                entry[1].update(verts)

    result = []
    for shape in order:
        e = grouped[shape]
        result.append((shape, e[0], e[1]))
    return result


def _bake_one(target_shape, face_filter, vert_filter, source_shape,
              source_grid=None, source_positions=None, source_normals=None,
              kernel_radius=None, max_samples=8):
    """
    face_filter / vert_filter 均为 set 或 None.
        - 都是 None: 整 shape 处理
        - face_filter 不为 None: 这些 face 上的 face-vertex 都要处理
        - vert_filter 不为 None: 这些 vertex 涉及的 face-vertex 都要处理
        - 两者都有: 取并集 (任一命中即处理)
    """
    target_dag = _get_dag(target_shape)
    target_fn = om.MFnMesh(target_dag)
    target_xform = cmds.listRelatives(target_shape, parent=True, fullPath=True)[0]
    short = target_xform.split("|")[-1]

    n_verts = target_fn.numVertices
    is_full = (face_filter is None) and (vert_filter is None)

    # 需要做法线混合的顶点集合: vert_filter 中的顶点 + face_filter 各面的顶点
    if is_full:
        blend_verts = None
    else:
        blend_verts = set()
        if vert_filter:
            blend_verts.update(vert_filter)
        if face_filter:
            for fid in face_filter:
                try:
                    blend_verts.update(target_fn.getPolygonVertices(fid))
                except Exception:
                    pass

    # ---------- 1) 读 A 原本法线 ----------
    a_normals = _get_vertex_normals_world(target_fn, target_dag)

    # ---------- 2) Elendt 核在 B 上做加权采样, 只对需要混合的顶点查询 ----------
    src_dag = _get_dag(source_shape)
    src_fn = om.MFnMesh(src_dag)
    c_normals = [None] * n_verts
    iter_verts = range(n_verts) if blend_verts is None else blend_verts
    for vid in iter_verts:
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

    # ---------- 3) 读 A 的 R 通道作为遮罩, 在 world space 用 R 线性混合 ----------
    r_mask = _get_vertex_r_mask(target_fn)
    if sum(1 for r in r_mask if r > 1e-4) == 0:
        cmds.warning(u"[BakeNormalWithMask] {0} 的顶点色 R 通道全为 0, 混合后法线和原模型完全一样, "
                     u"请检查目标 mesh 的 current color set".format(short))

    final_world_normals = [None] * n_verts
    for vid in range(n_verts):
        a_n = a_normals[vid]
        if blend_verts is not None and vid not in blend_verts:
            final_world_normals[vid] = a_n
            continue
        c_n = c_normals[vid] if c_normals[vid] is not None else a_n
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

    if DEBUG:
        # ---------- [DEBUG] 跳过切线转换/顶点色, 直接 setVertexNormals 到 A 上 ----------
        if blend_verts is None:
            write_verts = list(range(n_verts))
        else:
            write_verts = sorted(blend_verts)
        try:
            cmds.polyNormalPerVertex(
                ["{0}.vtx[{1}]".format(target_shape, v) for v in write_verts],
                unFreezeNormal=True,
            )
        except Exception:
            pass

        normals_array = om.MFloatVectorArray()
        vid_array = om.MIntArray()
        for vid in write_verts:
            nv = final_world_normals[vid]
            normals_array.append(om.MFloatVector(nv.x, nv.y, nv.z))
            vid_array.append(vid)
        target_fn.setVertexNormals(normals_array, vid_array, om.MSpace.kWorld)
        target_fn.updateSurface()
        return

    # ---------- 4) 逐 face-vertex 计算 TBN -> 切线空间法线 -> octahedral 编码成 (u, v) -----
    #   - 用 MFnMesh.getFaceVertexTangent (MikkT, 与 shader 端一致), 不用迭代器的 getTangent
    #   - 命中条件: 整 shape, 或 fid 在 face_filter, 或 vid 在 vert_filter
    #   - 按 MItMeshFaceVertex 迭代顺序填入 fv_uvs, 后面 setUVs + assignUVs (identity uvIds),
    #     共享同一 vertexId 的不同 face 各有独立 UV slot
    has_uv = False
    try:
        has_uv = target_fn.numUVs() > 0
    except Exception:
        has_uv = False
    if not has_uv:
        cmds.warning(u"[BakeNormalWithMask] {0} 没有 UV, 切线空间无定义, 结果可能不可用".format(short))

    fv_uvs = []

    it = om.MItMeshFaceVertex(target_dag)
    while not it.isDone():
        vid = it.vertexId()
        fid = it.faceId()
        hit = is_full
        if not hit and face_filter is not None and fid in face_filter:
            hit = True
        if not hit and vert_filter is not None and vid in vert_filter:
            hit = True

        if hit:
            try:
                T_raw = target_fn.getFaceVertexTangent(fid, vid, om.MSpace.kWorld)
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
            fv_uvs.append(_octahedral_encode(nt))
        else:
            fv_uvs.append(None)
        it.next()

    # ---------- 5) 写入 A 的 face-vertex UV (新 UV set: ENCODED_NORMAL_UV_SET) -----------
    _write_face_vertex_uvs(target_fn, ENCODED_NORMAL_UV_SET, fv_uvs)


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
    for shape, face_filter, vert_filter in grouped:
        try:
            _bake_one(
                shape, face_filter, vert_filter, source_shape,
                source_grid=grid,
                source_positions=src_positions,
                source_normals=src_normals,
                kernel_radius=kernel_radius,
                max_samples=max_samples,
            )
            ok += 1
            if face_filter is None and vert_filter is None:
                n_info = u"全部"
            else:
                parts = []
                if face_filter is not None:
                    parts.append(u"{0} 面".format(len(face_filter)))
                if vert_filter is not None:
                    parts.append(u"{0} 顶点".format(len(vert_filter)))
                n_info = u" + ".join(parts)
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
    bake_normal_with_mask(kernel_radius=10, max_samples=2)
