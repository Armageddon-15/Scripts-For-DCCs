import maya.api.OpenMaya as om2
from .core import OM_SelectionUtil as omUtil
from .core import ObjectTransformation as ObjTrans
import pymel.core as core
import pymel.core.datatypes as pmdt


class SymmetryData:
    def __init__(self, source_id: int, source_pos: om2.MPoint, source_sym_pos: om2.MPoint, dest_id: int):
        self.source_id = source_id
        self.source_pos = source_pos
        self.source_sym_pos = source_sym_pos
        self.dest_id = dest_id

    def __str__(self):
        st = (f"source id : {self.source_id} | "
              f"source position: {self.source_pos} | "
              f"source symmetry position: {self.source_sym_pos} | "
              f"dest id : {self.dest_id}\n")
        return st

    def __repr__(self):
        return self.__str__()

def maya_useNewAPI():
    """
    Tell Maya use open maya 2
    """
    pass


def getFlipPosition(position: om2.MPoint, plane_position: om2.MPoint, plane_normal: om2.MVector) -> om2.MPoint:
    new_pos = position - plane_position
    reverse_normal = plane_normal * -1.0
    d = new_pos * plane_normal
    return om2.MPoint(d*reverse_normal*2+om2.MVector(position))


def getFlipVertex(plan_pos: om2.MPoint=om2.MPoint(0, 0, 0), plan_normal:om2.MVector = om2.MVector(1, 0, 0)):
    sel: om2.MSelectionList = omUtil.convertSelectionToVertexSelection()

    flip_mat = om2.MMatrix.kIdentity
    flip_mat[0] = -1
    dag, component = sel.getComponent(0)
    dag.extendToShape()
    node = dag.node()
    matrix:om2.MMatrix = dag.inclusiveMatrix()
    print(matrix)
    intersector = om2.MMeshIntersector()
    intersector.create(node, matrix)

    vertex_iter = omUtil.getVertIterFromSelection(dag, component)
    p_iter = om2.MItMeshPolygon(dag)
    face_tris = [m.getTriangles() for m in p_iter]

    # id_dict = {}
    sym_data = []

    for vertex in vertex_iter:
        vertex_pos = vertex.position(space=om2.MSpace.kWorld)
        # flip_vertex = flip_mat * vertex_pos
        flip_pos = getFlipPosition(vertex_pos, plan_pos, plan_normal)
        print(vertex_pos, flip_pos)
        point_on_mesh: om2.MPointOnMesh = intersector.getClosestPoint(flip_pos)
        tris_vertices_id = face_tris[point_on_mesh.face][1]
        tri_ver_count_start = point_on_mesh.triangle*3
        hit_vertices = [tris_vertices_id[tri_ver_count_start], tris_vertices_id[tri_ver_count_start+1], tris_vertices_id[tri_ver_count_start+2]]
        b_a, b_b = point_on_mesh.barycentricCoords
        b_c = 1 - b_a -b_b
        ind = [b_a, b_b, b_c]
        print(hit_vertices, ind, point_on_mesh.point)
        ordered_ind = [i[0] for i in sorted(enumerate(ind), key=lambda x:x[1])]
        dest_id = hit_vertices[ordered_ind[2]]
        # id_dict.update({vertex.index():dest_id})
        sym_data.append(SymmetryData(vertex.index(), vertex_pos, flip_pos, dest_id))
        print(f"vertex id: {vertex.index()}, closest vertex id: {dest_id}", )

    return sym_data

def getExactSymmetryVertices(plan_pos: om2.MPoint=om2.MPoint(0, 0, 0), plan_normal:om2.MVector = om2.MVector(1, 0, 0), method = 1):
    """
    method 0 : first half - source
    method 1 : every other item is the source
    """
    sel = om2.MGlobal.getActiveSelectionList(True)

    dag, component = sel.getComponent(0)
    mesh = om2.MFnMesh(dag)

    id_list = []
    for i in range(sel.length()):
        dag, component = sel.getComponent(i)
        vertex_iter = omUtil.getVertIterFromSelection(dag, component)
        for vertex in vertex_iter:
            # print(vertex.index())
            id_list.append(vertex.index())
    # print(id_list)
    vertex_length = len(id_list)
    if vertex_length % 2 != 0:
        return
    vertex_length_half = int(vertex_length / 2)
    source_vert_ids = []
    symmetry_vertex_ids = []
    if method == 0:
        source_vert_ids = id_list[:vertex_length_half]
        symmetry_vertex_ids = id_list[vertex_length_half:]
    elif method == 1:
        source_vert_ids = id_list[::2]
        symmetry_vertex_ids = id_list[1::2]

    sym_data = []
    for i in range(len(source_vert_ids)):
        vert_id = source_vert_ids[i]
        vertex_pos = mesh.getPoint(vert_id, om2.MSpace.kWorld)
        flip_pos = getFlipPosition(vertex_pos, plan_pos, plan_normal)
        dest_id = symmetry_vertex_ids[i]
        sym_data.append(SymmetryData(vert_id, vertex_pos, flip_pos, dest_id))

    return sym_data



def symmetryVertices(method="spacial", plan_pos=None, plan_normal=None, exact_order_method="first_half"):
    if plan_normal is None:
        plan_normal = [1, 0, 0]
    if plan_pos is None:
        plan_pos = [0, 0, 0]
    plan_normal = om2.MVector(plan_normal)
    plan_pos = om2.MPoint(plan_pos)

    exact_order_method = int(exact_order_method != "first_half" )
    print(exact_order_method)
    obj = core.ls(sl = True)
    shape: core.nodetypes.Mesh = core.listRelatives(obj, parent=True)
    with core.UndoChunk("Symmetry"):
        # sym_data = []
        if method == "spacial":
            sym_data = getFlipVertex(plan_pos, plan_normal)
        else:
            sym_data = getExactSymmetryVertices(plan_pos, plan_normal, exact_order_method)
        for data in sym_data:
            dest_pos = [data.source_sym_pos[0], data.source_sym_pos[1], data.source_sym_pos[2]]
            print(dest_pos)
            shape[0].setPoint(data.dest_id, dest_pos, space="world")


def getCurrentSelectionPosition(space="world"):
    try:
        sel = core.ls(sl=True)[0]
    except IndexError:
        return pmdt.Vector(0, 0, 0)
        # print(type(sel), sel)
    return ObjTrans.getCurrentSelectionPosition(sel, space)



def getCurrentSelectionNormal(space="world"):
    v_up = pmdt.Vector(1, 0, 0)
    try:
        sel = core.ls(sl=True)[0]
    except IndexError:
        return v_up
    return ObjTrans.getCurrentSelectionNormal(sel, space)

