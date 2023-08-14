import core.Utils as Utils
import core.Component as Component
import core.SelectionUtil as SelecUtils
import core.ObjectTransformation as ObjTrans

import pymel.core as core
import pymel.core.nodetypes as pmnt
import pymel.core.datatypes as pmdt 

import random


def rotateVector(dir, dest_dir):
    rotate_axis = pmdt.normal(pmdt.cross(dir, dest_dir))
    rotate_angle = pmdt.acos(pmdt.dot(dir, dest_dir))
    
    return pmdt.Quaternion(rotate_angle, rotate_axis)


def getBordersFromBoarderEdges(border_edges):
    name = border_edges[0].__str__().split(".")[0]
    used_edge_indices = []
    final_edges = []
    
    for edge in border_edges:
        if edge.index() in used_edge_indices:
            continue
        
        edge_loop = Component.getEdgeLoopFromEdge(edge)
        used_edge_indices.extend(edge_loop)
        
        edges = []
        for ind in edge_loop:
            edge_name = name + ".e[%d]" % ind
            e = core.MeshEdge(edge_name)
            edges.append(e)
            
        if len(edges) > 0:
            final_edges.append(edges)
            
    return final_edges

    
def getBorderEdges(mesh):
    if type(mesh) is pmnt.Mesh:
        border_edges = core.polyListComponentConversion(mesh.faces, border=True, fromFace =True, toEdge=True)
        border_edges = [core.MeshEdge(b) for b in border_edges]
        separate_edges = []
        for edges in border_edges:
            separate_edges.extend(Component.getSeparateComponentFromSelection(edges, core.MeshEdge))
            
        border_loops = getBordersFromBoarderEdges(separate_edges)
        return border_loops
    

def getInformationFromEdgeLoop(edge_loop, space="world"):
    """
    return vertices, vertices position, center position and area_factors(for large-small only)

    """
    vtx = []
    for edge in edge_loop:
        vtx.extend(core.polyListComponentConversion(edge, fromEdge=True, toVertex=True))
        
    vertices = core.ls(vtx, flatten=True)
    vertices = Utils.uniqueList(vertices)
    
    pos = []
    for vert in vertices:
        pos.append(pmdt.Vector(vert.getPosition(space)))
    
    center_pos = Utils.average(pos)
    
    length = 0
    for p in pos:
        length += (p-center_pos).length()
        
    area_factor = length / len(pos)
    
    return vertices, pos, center_pos, area_factor


def alignPivotToEdgeLoop(pivot_axis_to_align, center_pos, loop_vertex_pos):
    rand_vert = []
    while len(rand_vert) != 3:
        vert = loop_vertex_pos[random.randint(0, len(loop_vertex_pos)-1)]
        if vert not in rand_vert:
            rand_vert.append(vert)
            
    pos0 = rand_vert[0]
    pos1 = rand_vert[1]
    pos2 = rand_vert[2]
    
    face_normal = pmdt.normal(pmdt.cross(pos1 - pos0, pos2 - pos0))
    
    new_rot = rotateVector(pivot_axis_to_align, face_normal)
    rot = new_rot.asEulerRotation().asVector() * (180/pmdt.pi)
    print(center_pos)
    core.manipPivot(o=rot)
    

def alignPivotToCertainTrans(align_axis_str="pivot_y", func=max, space="world"):
    sel = SelecUtils.orderedSeclect()
    mesh = ObjTrans.getTransformShapes(sel)[0]
    border_edges = getBorderEdges(mesh)
    
    area_list = []
    pos_list = []
    center_list = []

    for loop in border_edges:
        vertices, pos, center, area_factor = getInformationFromEdgeLoop(loop, space)
        pos_list.append(pos)
        center_list.append(center)
        area_list.append(area_factor)
    
    largest_list = Utils.getMostInList(area_list, func)
    largest_index = random.randint(0, len(largest_list)-1)
        
    final_pos_list = pos_list[largest_index]
    final_center = center_list[largest_index]
    certain_axis = Component.AXIS_VECTOR_DICT[align_axis_str]
    
    alignPivotToEdgeLoop(certain_axis, final_center, final_pos_list)   
    ObjTrans.setPivotPosition(sel[0], final_center) 


def secondaryAxisRotation(focus_dir, first_axis="pivot_y", second_axis="pivot_x"):
    current_pivot_rot = core.manipPivot(q=True, o=True)[0]
    current_pivot_rot = pmdt.EulerRotation(current_pivot_rot, unit="degrees").asQuaternion()
    first_pivot_axis = Component.AXIS_VECTOR_DICT[first_axis].rotateBy(current_pivot_rot)
    second_pivot_axis = Component.AXIS_VECTOR_DICT[second_axis].rotateBy(current_pivot_rot)
    
    project_length = pmdt.dot(focus_dir, first_pivot_axis) 
    new_dir = pmdt.normal(focus_dir - first_pivot_axis * project_length)
    rot_q = current_pivot_rot * rotateVector(second_pivot_axis, new_dir) 
    rot = rot_q.asEulerRotation().asVector() * (180/pmdt.pi)
    print(rot)
    core.manipPivot(o=rot)