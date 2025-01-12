from .core import Utils as Utils
from .core import Component as Component
from .core import SelectionUtil as SelecUtils
from .core import ObjectTransformation as ObjTrans
from .core import PyMelMath as PyMelMath
from .core import MelUtils as MelUtils
from .core import MayaWarning as MWaring

import pymel.core as core
import pymel.core.nodetypes as pmnt
import pymel.core.datatypes as pmdt 

import random

def getRealPivotRotation():
    vaild_pivot_rot = core.manipPivot(q=True, oriValid=True)
    if vaild_pivot_rot:
        current_pivot_rot = core.manipPivot(q=True, o=True)[0]
        current_pivot_rot = pmdt.EulerRotation(current_pivot_rot, unit="degrees").asQuaternion()
    else:
        obj = SelecUtils.orderedSelect()[0]
        current_pivot_rot = obj.getRotation(space="world", quaternion=True)
    return current_pivot_rot


def __getInformationFromEdgeLoop(edge_loop, space="world"):
    """
    return vertices, vertices' position, center position and area_factors(for large-small only)
    """
    vtx = []
    pos = []
    length = 0    
        
    for edge in edge_loop:
        vtx.extend(core.polyListComponentConversion(edge, fromEdge=True, toVertex=True))
    vertices = core.ls(vtx, flatten=True)
    # component is unhashable in py3 pymel
    vertices = Utils.uniqueListUnhash(vertices)
    for vert in vertices:
        pos.append(pmdt.Vector(vert.getPosition(space)))
    
    center_pos = Utils.average(pos)
    for p in pos:
        length += (p-center_pos).length()
        
    area_factor = length / len(pos)
    return vertices, pos, center_pos, area_factor


def __alignPivotToEdgeLoop(pivot_axis_to_align, loop_vertex_pos):
    if len(loop_vertex_pos) < 3:
        raise ValueError("Edges'vertices number less than 3")
    
    rand_vert = []
    while len(rand_vert) != 3:
        vert = loop_vertex_pos[random.randint(0, len(loop_vertex_pos)-1)]
        if vert not in rand_vert:
            rand_vert.append(vert)
            
    pos0 = rand_vert[0]
    pos1 = rand_vert[1]
    pos2 = rand_vert[2]
    
    face_normal = pmdt.normal(pmdt.cross(pos1 - pos0, pos2 - pos0))
    
    new_rot = PyMelMath.rotateVector(pivot_axis_to_align, face_normal)
    rot = PyMelMath.quaternionToDegreeEulerVector(new_rot)
    core.manipPivot(o=rot)
    

def alignPivotToCertainTrans(transform, align_axis=pmdt.Vector(0,1,0), func=max, set_trans=True, set_ori=True, space="world"):
    mesh = ObjTrans.getTransformShapes(transform)[0]
    border_edges = Component.getBorderEdges(mesh)
    
    if not len(border_edges) > 0:
        return None
    
    area_list = []
    pos_list = []
    center_list = []

    for loop in border_edges:
        vertices, pos, center, area_factor = __getInformationFromEdgeLoop(loop, space)
        pos_list.append(pos)
        center_list.append(center)
        area_list.append(area_factor)
    
    largest_in_list = Utils.getMostInList(area_list, func)
    largest_index = largest_in_list[random.randint(0, len(largest_in_list)-1)]
        
    final_pos_list = pos_list[largest_index]
    final_center = center_list[largest_index]
    if set_ori: __alignPivotToEdgeLoop(align_axis, final_pos_list)   
    if set_trans: ObjTrans.setPivotPosition(transform, final_center) 
    

def secondaryAxisRotation(focus_dir, first_axis="pivot_y", second_axis="pivot_x"):
    if second_axis in Component.AXIS_VECTOR_DICT:
        current_pivot_rot = getRealPivotRotation()
        first_pivot_axis = Component.AXIS_VECTOR_DICT[first_axis].rotateBy(current_pivot_rot)
        second_pivot_axis = Component.AXIS_VECTOR_DICT[second_axis].rotateBy(current_pivot_rot)
        
        project_length = pmdt.dot(focus_dir, first_pivot_axis) 
        new_dir = pmdt.normal(focus_dir - first_pivot_axis * project_length)
        rot_q = current_pivot_rot * PyMelMath.rotateVector(second_pivot_axis, new_dir) 
        rot = PyMelMath.quaternionToDegreeEulerVector(rot_q)
        # print(rot)
        core.manipPivot(o=rot)


def pivotAlignmentMainAxis(axis_key="pivot_y", func_method="max", set_trans=True, set_ori=True, bake=False, space="world"):
    """
    func_method can be: 
        max: transform mode, search the largest hole, 
        min: transform mode, search the smallest hole, 
        selected_loop: component mode, use selected edge loop to align the tranform pivot dir,
        ignore: componet mode, but just for modeling
    """
    sel = SelecUtils.orderedSelect()
    certain_axis = Component.AXIS_VECTOR_DICT[axis_key]
    
    with core.UndoChunk("align primary pivot axis to edge loop"):
        if type(sel[0]) is not pmnt.Transform:
            vertices, pos, center, area_factor = __getInformationFromEdgeLoop(sel, space)
            if func_method != "ignore":
                name = sel[0].__str__().split(".")[0]
                transform = ObjTrans.getShapeTransforms(pmnt.Mesh(name))[0]
                if set_trans: 
                    transform.setPivots(center, worldSpace=True)
                    # print(transform, center)
                SelecUtils.select(transform)
            else:
                if set_trans: core.manipPivot(p=center)  
            if set_ori: __alignPivotToEdgeLoop(certain_axis, pos)
            
        else:
            method_dict = {"max": max, "min": min}
            if func_method in method_dict:
                for obj in sel:
                    SelecUtils.select(obj)
                    alignPivotToCertainTrans(obj, certain_axis, method_dict[func_method], set_trans, set_ori, space)
                    if bake and len(sel) > 1:
                        bakePivot()
                return None
            raise TypeError("method should be max or min")
        
        
def pivotAlignmentSecondaryAxis(axis_key="world_x", secondary_axis="pivot_x", main_axis="pivot_y", custom_pos=[0,0,0]):
    """
    axis_key can be:
        pivot_x, pivot_y, pivot_z,
        custom_pos: use input: custom_pos
        ignore: do nothing
    """
    # if axis_key in {"world_x", "world_y", "world_z"}:
    axis_key.replace("world", "pivot")
    if axis_key == "ignore":
        return None
    if axis_key in Component.AXIS_VECTOR_DICT:
        focus_dir = Component.AXIS_VECTOR_DICT[axis_key]
    else:
        aim_pos = pmdt.Vector(custom_pos)
        sel = SelecUtils.orderedSelect()[0]
        if type(sel) is pmnt.Transform:
            pivot_pos = ObjTrans.getPivotPosInWorldSpace(sel)
        else:
            pivot_pos = pmdt.Vector(core.manipPivot(q=True, p=True)[0])
            pos_valid = core.manipPivot(q=True, posValid=True)
            if not pos_valid: 
                MWaring.warning("Cannot get correct pivot position when pivot not modified, please mannully make a custom pivot")
                
        focus_dir = (aim_pos - pivot_pos).normal()
    with core.UndoChunk("align secondary pivot axis to certain direction"):
        secondaryAxisRotation(focus_dir, main_axis, secondary_axis)
    
    
def bakePivot():
    MelUtils.bakeCustomPivot()
    
        
def zeroRotation():

    with core.UndoChunk("zero all transform rotation"):
        sel = SelecUtils.orderedSelect()
        for obj in sel:
            if not type(obj) is pmnt.Transform:
                return None
            obj.setRotation(pmdt.Vector(0,0,0))
    

def invertPivotAxis(first_axis="pivot_y", second_axis="pivot_x"):
    current_pivot_rot = getRealPivotRotation()
        
    if second_axis in Component.AXIS_VECTOR_DICT:
        second_pivot_axis = Component.AXIS_VECTOR_DICT[second_axis].rotateBy(current_pivot_rot)
        rot = current_pivot_rot*pmdt.Quaternion(pmdt.pi, second_pivot_axis)
    else:
        first_pivot_axis = Component.AXIS_VECTOR_DICT[first_axis].rotateBy(current_pivot_rot)
        rot = current_pivot_rot*PyMelMath.rotateVector(first_pivot_axis, -first_pivot_axis)
    
    rot = PyMelMath.quaternionToDegreeEulerVector(rot)
    core.manipPivot(o=rot) 


def invertPivotsAxis(first_axis="pivot_y", second_axis="pivot_x"):
    sel = SelecUtils.orderedSelect()
    for obj in sel:
        invertPivotAxis(obj, first_axis, second_axis)
           

def getCurrentSelectionPositon(space="world"):
    def theFunc():
        try:
            sel = SelecUtils.orderedSelect()[0]
        except IndexError:
            return pmdt.Vector(0, 0, 0) 
        # print(type(sel), sel)
        if type(sel) is pmnt.Transform:
            return ObjTrans.getTransformPosition(sel)
        elif type(sel) is pmnt.Mesh:
            return ObjTrans.getTransformPosition(ObjTrans.getShapeTransforms(sel)[0], space)
        elif type(sel) is core.MeshVertex:
            # print(sel, sel.getPosition(space))
            return sel.getPosition(space)
        elif type(sel) is core.MeshEdge:
            return Utils.average2(pmdt.Vector(sel.getPoint(0, space)), pmdt.Vector(sel.getPoint(1, space)))
        elif type(sel) is core.MeshFace:
            points = sel.getPoints(space)
            new_v = []
            for point in points:
                new_v.append(pmdt.Vector(point))
            return Utils.average(new_v)
        else:
            return pmdt.Vector(0, 0, 0)
        
    return pmdt.Vector(theFunc())

        
        