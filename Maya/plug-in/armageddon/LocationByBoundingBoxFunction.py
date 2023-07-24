import core.ObjectTransformation as ObjTrans
import core.SelectionUtil as SelectUtils
import core.Utils as Utils

import pymel.core as core
import pymel.core.nodetypes as pmnt
import pymel.core.datatypes as pmdt 


def groupMoveToWorldCenter(states):
    sel = SelectUtils.orderedSeclect()
    if len(sel) > 0:
        bbox = ObjTrans.getAllTransformsBoundingBox(sel)
        aim_pos = ObjTrans.bboxCertainPostionByState(bbox, states, pmdt.Point([0,0,0]))
        final_group = SelectUtils.keepTopMostSelectedTransform(sel)
        
        with core.UndoChunk("group move to world center"):
            for obj in final_group:
                obj.translateBy(-pmdt.Vector(aim_pos), space="world")
        

def groupMoveToWorldCenterByPivot():
    sel = SelectUtils.orderedSeclect()
    if len(sel) > 0:
        final_group = SelectUtils.keepTopMostSelectedTransform(sel)
        for obj in final_group:
            pivot_pos = obj.getPivots(ws=True)[0]
            obj.translateBy(-pmdt.Vector(pivot_pos), space="world")