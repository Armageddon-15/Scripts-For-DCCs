from .core import ObjectTransformation as ObjTrans
from .core import SelectionUtil as SelectUtils
from .core import Utils as Utils

import pymel.core as core
import pymel.core.nodetypes as pmnt
import pymel.core.datatypes as pmdt 


def __excludeChildrenReturnLocation(selected_obj, children_obj, parent_sel, offset):
    for obj in children_obj:
        obj_sel = obj in selected_obj
        
        obj_offset = offset
        if parent_sel != obj_sel:
            obj_offset = -offset
            obj.translateBy(obj_offset, space="world")
        
        children = ObjTrans.getTransformChildren(obj)
        if len(children) > 0:
            __excludeChildrenReturnLocation(selected_obj, children, obj_sel, obj_offset)
            

def __getBBoxAimPosition(o, states, actual_size, bbox_exclude_children):
    bbox = ObjTrans.getSingleTransformBoundingBox(o, actual_size, bbox_exclude_children)
    aim_pos = ObjTrans.bboxCertainPostionByState(bbox, states)
    return aim_pos

     
def __excludeChidrenTranslation(sel, root_group, move_exclude_children, translate_func):
    for root in root_group:
        all_children = ObjTrans.getTransformAllChildren(root, with_self=True)
        current_pos_dict = {}
        for child in all_children:
            current_pos_dict.update({child: pmdt.Vector(ObjTrans.getTransformPosition(child))})
            
        for child in all_children:
            if child in sel:
                translate_func(child)
            elif move_exclude_children:
                ObjTrans.setTransformPosition(child, current_pos_dict[child])
            
            
def moveToWorldCenterByGroupBBox(states, move_exclude_children, actual_size=True, 
                                 bbox_exclude_children=False):
    sel = SelectUtils.orderedSeclect()
    if len(sel) > 0:
        with core.UndoChunk("group move to world center"):        
            root_group = SelectUtils.keepTopMostSelectedTransform(sel)        
            bbox = ObjTrans.getAllTransformsBoundingBox(sel, actual_size, bbox_exclude_children)
            aim_pos = ObjTrans.bboxCertainPostionByState(bbox, states, pmdt.Point([0,0,0]))
            for obj in root_group:
                obj.translateBy(-pmdt.Vector(aim_pos), space="world")
                if move_exclude_children:
                    print(obj, obj in sel)
                    __excludeChildrenReturnLocation(sel, ObjTrans.getTransformChildren(obj),
                                                  obj in sel, -pmdt.Vector(aim_pos))

            SelectUtils.select(sel)
            
            
def eachMoveToWorldCenterByEachBBox(states, move_exclude_children, actual_size=True, 
                                    bbox_exclude_children=False):

    def translateFunc(o):
        aim_pos = __getBBoxAimPosition(o, states, actual_size, bbox_exclude_children)
        o.translateBy(-pmdt.Vector(aim_pos), space="world")
    
    sel = SelectUtils.orderedSeclect()
    if len(sel) > 0:
        with core.UndoChunk("each move to world center"):
            root_group = SelectUtils.keepTopMostSelectedTransform(sel)
            __excludeChidrenTranslation(sel, root_group, move_exclude_children, translateFunc)
            SelectUtils.select(sel)
            

def setPivotByBoundingBox(states, one_large_bbox=True, bbox_actual_size=True, 
                          bbox_exclude_children=False):
    sel = SelectUtils.orderedSeclect()
    if len(sel) > 0:
        with core.UndoChunk("set pivot by bounding box"):        
            if one_large_bbox:
                bbox = ObjTrans.getAllTransformsBoundingBox(sel, bbox_actual_size, bbox_exclude_children)
    
            for obj in sel:
                if not one_large_bbox:
                    bbox = ObjTrans.getSingleTransformBoundingBox(obj, bbox_actual_size, bbox_exclude_children)
                
                current_pivot_pos = ObjTrans.getPivotPosition(obj)
                aim_pos = ObjTrans.bboxCertainPostionByState(bbox, states, current_pivot_pos)
                ObjTrans.setPivotPosition(obj, aim_pos)
            
            SelectUtils.select(sel)
        

def moveToWorldCenterByPivot(move_exclude_children, keep_pivot_offset=False):
    
    def tranlateFunc(o):
        pivot_pos = pmdt.Point(ObjTrans.getTransformPivot(o))
        o.translateBy(-pmdt.Vector(pivot_pos), space="world")
        if not keep_pivot_offset:
            ObjTrans.setPivotPosition(o, pivot_pos)
    
    sel = SelectUtils.orderedSeclect()
    if len(sel) > 0:
        root_group = SelectUtils.keepTopMostSelectedTransform(sel)
        with core.UndoChunk("translate to world center by pivot"):
            __excludeChidrenTranslation(sel, root_group, move_exclude_children, tranlateFunc)


def moveToPivotByBBox(states, move_exclude_children, keep_pivot_offset=False,
                      bbox_actual_size=True, bbox_exclude_children=False):

    def translateFunc(o):
        pivot_pos = ObjTrans.getPivotPosition(o)
        bbox_aim_pos = __getBBoxAimPosition(o, states, bbox_actual_size, bbox_exclude_children)
        if not keep_pivot_offset:      
            ObjTrans.setPivotPosition(o, bbox_aim_pos)  
        offset = pmdt.Vector(pivot_pos) - pmdt.Vector(bbox_aim_pos)
        o.translateBy(offset, space="world")

    sel = SelectUtils.orderedSeclect()
    if len(sel) > 0:
        root_group = SelectUtils.keepTopMostSelectedTransform(sel)
        with core.UndoChunk("move selected to pivot by bounding box"):
            __excludeChidrenTranslation(sel, root_group, move_exclude_children, translateFunc)
            SelectUtils.select(sel)


def visualizeSelectedBoundingBox(one_large_bbox=True, bbox_actual_size=True, bbox_exclude_children=False):
    sel = SelectUtils.orderedSeclect()
    if len(sel) > 0:
        with core.UndoChunk("visualize selected bounding box"):
            if one_large_bbox:
                bbox = ObjTrans.getAllTransformsBoundingBox(sel, bbox_actual_size, bbox_exclude_children)
                ObjTrans.visualizeBoundingBox(bbox)
            else:
                vis_bbxes = []
                for obj in sel:
                    bbox = ObjTrans.getSingleTransformBoundingBox(obj, bbox_actual_size, bbox_exclude_children)
                    bbox_name_suffix = obj.__melobject__()
                    vis_bbxes.append(ObjTrans.visualizeBoundingBox(bbox, "BBoxVis_" + bbox_name_suffix)[0])
                SelectUtils.select(vis_bbxes)