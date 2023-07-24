import Utils
import SelectionUtil

import pymel.core as core
import pymel.core.nodetypes as pmnt
import pymel.core.datatypes as pmdt 


def getShapeTransforms(shape):
    return core.listRelatives(shape, parent=True)


def getTransformShapes(transform):
    return core.listRelatives(transform, shapes=True)


def getComponetsTransforms(cs):
    c = Utils.uniqueList(SelectionUtil.shapeSelect(cs))
    return getShapeTransforms(c)


def getTransformPosition(transform, world_space=True):
    return transform.getPivot(worldSpace=world_space)



def keepTopMostSelectedTransform(selection):
    selected_top_parent_set = set()

    for obj in selection:
        if type(obj) is pmnt.Transform:
            parents = obj.getAllParents()
            if len(parents) > 0:
                all_not_in_sel = True
                for p in reversed(parents):
                    if p in selection:
                        all_not_in_sel = False
                        selected_top_parent_set.add(p)
                        break
                if all_not_in_sel:
                    selected_top_parent_set.add(obj)
            else:
                selected_top_parent_set.add(obj)
    return list(selected_top_parent_set)


def getSingleTransformBoundingBox(transform, space="world"):
    if type(transform) is pmnt.Transform:
        return transform.getBoundingBox(space=space)
    
    return pmdt.BoundingBox()


def largestBoundingBoxOfBoundingBoxes(bboxes):
    box_min = bboxes[0].min()
    box_max = bboxes[0].max()
    
    for i in range(len(bboxes) - 1):
        bbox_min = bboxes[i+1].min()
        bbox_max = bboxes[i+1].max()
        
        box_min.x = min(bbox_min.x, box_min.x)
        box_min.y = min(bbox_min.y, box_min.y)        
        box_min.z = min(bbox_min.z, box_min.z)
        
        box_max.x = max(bbox_max.x, box_max.x)         
        box_max.y = max(bbox_max.y, box_max.y)
        box_max.z = max(bbox_max.z, box_max.z)
        
    return pmdt.BoundingBox(box_min, box_max)        
    
      
    
def getAllTransformsBoundingBox(transforms, space="world"):
    bboxes = []
    
    for trans in transforms:
        bboxes.append(getSingleTransformBoundingBox(trans, space))
        
    return largestBoundingBoxOfBoundingBoxes(bboxes)


def visualizeBoundingBox(bbox, name="BoundingBoxVis"):
    with core.UndoChunk("create visual bounding box"):
        vis_cube = core.polyCube(d=bbox.depth(), w=bbox.width(), h=bbox.height(), name=name)
        vis_cube_trans = vis_cube[0]
        vis_cube_trans.setTranslation(bbox.center())
    return vis_cube
        

def getBoundingBoxCertainAxisPosition(bbox, axis, state):
    if type(bbox) is pmdt.BoundingBox:
        bbox_list = bbox.__melobject__()
    elif type(bbox) is list:
        bbox_list = bbox
    else:
        raise TypeError("bbox type: ", type(bbox), "is not bbox or list")        
    
    if state == u"Min":
        return bbox_list[axis]
    elif state == u"Max":
        return bbox_list[axis + 3]
    elif state == u"Mid":
        return Utils.average2(bbox_list[axis], bbox_list[axis + 3])

    return None


def bboxCertainPostionByState(bbox, states, current_pivot_position=pmdt.Point()):
    if type(bbox) is pmdt.BoundingBox:
        bbox_list = bbox.__melobject__()
    elif type(bbox) is list:
        bbox_list = bbox
    else:
        raise TypeError("bbox type: ", type(bbox), "is not bbox or list")    
    
    new_pivot_pos = []
    
    i=0
    for state in states:
        a = getBoundingBoxCertainAxisPosition(bbox_list, i, state)
        if a is not None:
            new_pivot_pos.append(a)
        else:
            new_pivot_pos.append(current_pivot_position.__melobject__()[i])
        i += 1
        
    return pmdt.Point(new_pivot_pos)