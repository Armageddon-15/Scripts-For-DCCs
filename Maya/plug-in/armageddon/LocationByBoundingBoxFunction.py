import core.ObjectTransformation as ObjTrans
import core.SelectionUtil as SelectUtils
import core.Utils as Utils

import pymel.core as core
import pymel.core.nodetypes as pmnt
import pymel.core.datatypes as pmdt 



def excludeChildrenReturnLocation(selected_obj, children_obj, parent_sel, offset):
    for obj in children_obj:
        obj_sel = False
        if obj in selected_obj:        
            obj_sel = True
        
        obj_offset = offset
        if parent_sel != obj_sel:
            obj_offset = -offset
            obj.translateBy(obj_offset, space="world")
        
        children = ObjTrans.getTransformChildren(obj)
        if len(children) > 0:
            excludeChildrenReturnLocation(selected_obj, children, obj_sel, obj_offset)
        




def groupMoveToWorldCenter(states, move_exclue_children, actual_size=True, bbox_exclude_children=False):
    sel = SelectUtils.orderedSeclect()
    if len(sel) > 0:
        root_group = SelectUtils.keepTopMostSelectedTransform(sel)        
        bbox = ObjTrans.getAllTransformsBoundingBox(sel, actual_size, bbox_exclude_children)
        # ObjTrans.visualizeBoundingBox(bbox)
        aim_pos = ObjTrans.bboxCertainPostionByState(bbox, states, pmdt.Point([0,0,0]))

        with core.UndoChunk("group move to world center"):
            for obj in root_group:
                obj.translateBy(-pmdt.Vector(aim_pos), space="world")
                if move_exclue_children:
                    print(obj, obj in sel)
                    excludeChildrenReturnLocation(sel, ObjTrans.getTransformChildren(obj),
                                                  obj in sel, -pmdt.Vector(aim_pos))

                            
                
            name_list = []
            for obj in sel:
                name_list.append(obj.__melobject__())

            core.select(name_list)
        

def groupMoveToWorldCenterByPivot():
    sel = SelectUtils.orderedSeclect()
    if len(sel) > 0:
        final_group = SelectUtils.keepTopMostSelectedTransform(sel)
        for obj in final_group:
            pivot_pos = obj.getPivots(ws=True)[0]
            obj.translateBy(-pmdt.Vector(pivot_pos), space="world")