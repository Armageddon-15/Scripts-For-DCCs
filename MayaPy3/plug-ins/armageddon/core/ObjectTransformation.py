import Utils

import pymel.core as core
import pymel.core.nodetypes as pmnt
import pymel.core.datatypes as pmdt 


def getShapeTransforms(shape):
    return core.listRelatives(shape, parent=True)


def getTransformShapes(transform):
    return core.listRelatives(transform, shapes=True)


def getTransformChildren(transform, transform_only=True):
    children = core.listRelatives(transform, children=True)
    if not transform_only:
        return children        

    final_list = []
    for child in children:
        if type(child) is pmnt.Transform:
            final_list.append(child)
    return final_list


def getTransformAllChildren(transform, transform_only=True, with_self=False):
    children = getTransformChildren(transform, transform_only)
    child_list = []    
    if with_self:
        child_list = [transform]
        
    if len(children) > 0:
        for child in children:
            ch = getTransformAllChildren(child, transform_only)
            child_list.append(child)
            child_list.extend(ch)
                
    return child_list


def getPivotPosInWorldSpace(transform):
    return pmdt.Vector(core.xform(transform, q=True, piv=True, ws=True)[:3])


def getComponetsTransforms(shape):
    c = Utils.uniqueList(shape)
    return getShapeTransforms(c)


def getTransformPosition(transform, space="world"):
    return transform.getTranslation(space=space)


def setTransformPosition(transform, position, space="world"):
    return transform.setTranslation(position, space=space)


def getTransformPivot(transform, world_space=True):
    return transform.getPivots(worldSpace=world_space)[0]


def setPivotPosition(obj, posiiton, if_world_space=True):
    if type(obj) is pmnt.Transform:    
        core.xform(obj, pivots=posiiton, worldSpace=if_world_space)
        

def getPivotPosition(obj, if_world_space=True):
    if type(obj) is pmnt.Transform:    
        p = core.xform(obj, q=True, pivots=True, worldSpace=if_world_space)
        return pmdt.Point(p[:3])
    return pmdt.Point()


def getSingleTransformBoundingBox(transform=pmnt.Transform(), actual_size=True, 
                                  exclude_children=False, space="world"):
    if type(transform) is pmnt.Transform:
        if not exclude_children:
            if not actual_size:
                return transform.getBoundingBox(space=space)
            
        acopy = core.duplicate(transform)[0]
        core.parent(acopy, world=True)            
        
        if exclude_children:
            children = getTransformChildren(acopy)
            if len(children) > 0:
                for child in children:
                    # since "parent|child" name is not support in pymel,
                    # use string instead
                    child_name = child.__melobject__()
                    core.delete(child_name)
        if actual_size:
            core.makeIdentity(acopy, apply=True)
        bbox = acopy.getBoundingBox(space=space)
        core.delete(acopy)
        return bbox
        
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
    
    
def getAllTransformsBoundingBox(transforms, actual_size=True, exclude_children=False, space="world"):
    bboxes = []
    
    if type(transforms) is list:
        for trans in transforms:
            bboxes.append(getSingleTransformBoundingBox(trans, actual_size, exclude_children, space))
    elif type(transforms) is pmnt.Transform:
        return getSingleTransformBoundingBox(transforms, actual_size, exclude_children, space)
        
    return largestBoundingBoxOfBoundingBoxes(bboxes)


def getShapeBoundingBox(shape):
    shape_bbox_min = shape.boundingBoxMin.get()
    shape_bbox_max = shape.boundingBoxMax.get()
    
    return pmdt.BoundingBox(shape_bbox_min, shape_bbox_max)


def getTransformShapesBoundingBox(transform):
    if type(transform) is pmnt.Transform:
        shapes = getTransformShapes(transform)
        bboxes = []
        for shape in shapes:
            bboxes.append(getShapeBoundingBox(shape))
        
        return largestBoundingBoxOfBoundingBoxes(bboxes)
    return pmdt.BoundingBox()
            

def visualizeBoundingBox(bbox, name="BoundingBoxVis"):
    with core.UndoChunk("create visual bounding box"):
        vis_cube = core.polyCube(d=max(0.0001, bbox.depth()), 
                                 w=max(0.0001, bbox.width()), 
                                 h=max(0.0001, bbox.height()),
                                 sx=2, sy=2, sz=2, name=name)
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


