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


def getSingleTransformBoundingBox(transform, space="world"):
    if type(transform) is pmnt.Transform:
        return transform.getBoundingBox(space=space)
    
    return pmdt.BoundingBox()
    
    
def getAllTransformsFinalBoundingBox(transforms, space="world"):
    box_min = getSingleTransformBoundingBox(transforms[0], space).min()
    box_max = getSingleTransformBoundingBox(transforms[0], space).max()
    
    for i in range(len(transforms) - 1):
        bbox = getSingleTransformBoundingBox(transforms[i+1], space)
        bbox_min = bbox.min()
        bbox_max = bbox.max()
        
        box_min.x = min(bbox_min.x, box_min.x)
        box_min.y = min(bbox_min.y, box_min.y)        
        box_min.z = min(bbox_min.z, box_min.z)
        
        box_max.x = max(bbox_max.x, box_max.x)         
        box_max.y = max(bbox_max.y, box_max.y)
        box_max.z = max(bbox_max.z, box_max.z)         
        
        
    return pmdt.BoundingBox(box_min, box_max)


def visualizeBoundingBox(bbox):
    with core.UndoChunk("create visual bounding box"):
        vis_cube = core.polyCube(d=bbox.depth(), w=bbox.width(), h=bbox.height())
        vis_cube_trans = vis_cube[0]
        vis_cube_trans.setTranslation(bbox.center())