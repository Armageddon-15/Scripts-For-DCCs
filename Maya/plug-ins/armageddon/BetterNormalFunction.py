import maya.api.OpenMaya as om2
import pymel.core as core

import core.OM_SelectionUtil as OMSelUtil


def maya_useNewAPI():
    """
    Tell Maya use open maya 2
    """
    pass


def mergeTinyNormal(origin_normal, new_normal, threshold):
    project = origin_normal * new_normal
    if project + threshold >= 1:
        return True, origin_normal
    return False, new_normal


def alignTinyVertexNormalToFace(vertex_normal, faces, face_normals, threshold):
    if threshold > 0:
        for face_id in faces:
            face_normal = face_normals[face_id]
            state, normal = mergeTinyNormal(face_normal, vertex_normal, threshold)
            if state: 
                vertex_normal = normal
                break
            
    return vertex_normal


def vertexNormalFormFaceAttribute(vertex_position, connect_faces, 
                                  scaled_polygon_area, polygon_normal, polygon_center,
                                  area_weight, distance_weight, size_scale):
    
    new_normal = om2.MVector()
    for face_id in connect_faces:
        poly_area = scaled_polygon_area[face_id]
        poly_normal = polygon_normal[face_id]
        poly_center = polygon_center[face_id]
        distance = (poly_center - vertex_position).length()
        
        distance *= size_scale
        
        dist_fin = pow(distance, distance_weight)
        area_fin = pow(poly_area, area_weight)
        
        new_normal += (dist_fin + area_fin) * poly_normal
        
    new_normal.normalize()
    return new_normal


def getPolygonAttribute(shape_path, size_scale = 1, space=om2.MSpace.kObject):
    polygon_iter = om2.MItMeshPolygon(shape_path)
    
    polygon_area = []
    polygon_center = []
    polygon_normal = []
    for poly in polygon_iter:
        polygon_area.append(poly.getArea(space=space) * size_scale)
        polygon_center.append(poly.center(space=space))
        polygon_normal.append(poly.getNormal(space=space))
        
    return polygon_area, polygon_center, polygon_normal


def betterNormalNoSelection(shape_path, comp_type, threshold = 0.01, area_weight = 1,
                            distance_weight = 1, size_scale = 1, space=om2.MSpace.kObject):

    vertex_iter = OMSelUtil.getVertIterFromSelection(shape_path, comp_type)
    if vertex_iter is None:
        raise TypeError("Vertex Type Wrong")
    
    polygon_area, polygon_center, polygon_normal = getPolygonAttribute(shape_path, size_scale, space)

    new_vert_normals = om2.MVectorArray()
    
    new_vert_list = []
    for vertex in vertex_iter:
        vertex_position = vertex.position(space=space)
        connect_faces = vertex.getConnectedFaces()
        new_normal = vertexNormalFormFaceAttribute(vertex_position, connect_faces, 
                                                polygon_area, polygon_normal, polygon_center,
                                                area_weight, distance_weight, size_scale)
        new_normal = alignTinyVertexNormalToFace(new_normal, connect_faces, polygon_normal,
                                                    threshold)
        new_vert_normals.append(new_normal)
        
        new_vert_list.append(vertex.index())
        
    shape = om2.MFnMesh(shape_path)            
    shape.setVertexNormals(new_vert_normals, new_vert_list)
  
               
class BetterNormalBackend:
    def __init__(self):
        self.sel = None
        
    def updateSelection(self):
        self.sel = OMSelUtil.convertSelectionToVertexSelection()
            
    def releaseSelection(self):
        self.sel = None        
        
    def betterNormalExcute(self, threshold = 0.01, area_weight = 1, distance_weight = 1, 
                           size_scale = 1, space=om2.MSpace.kObject):
        if not self.sel is None and self.sel.length() > 0:
            for i in range(self.sel.length()):
                shape_path, comp = self.sel.getComponent(i)
                betterNormalNoSelection(shape_path, comp, threshold, area_weight,
                                        distance_weight, size_scale, space)
                
    def betterNormalExecuteOnce(self, threshold = 0.01, area_weight = 1, distance_weight = 1, 
                                size_scale = 1, space=om2.MSpace.kObject):
        if not self.sel is None and self.sel.length() > 0: 
            with core.UndoChunk("better normal"):
                for i in range(self.sel.length()):
                    shape_path, comp = self.sel.getComponent(i)
                    betterNormalNoSelection(shape_path, comp, threshold, area_weight,
                                            distance_weight, size_scale, space)  
                    
            self.releaseSelection()
        else:
            betterNormal(threshold, area_weight, distance_weight, size_scale, space) 

        
def updateBackendSelection():
    _bnb.updateSelection()
    
    
def releaseBackendSelection():
    _bnb.releaseSelection()
    
            
def betterNormalExecuteOnce(threshold = 0.01, area_weight = 1, distance_weight = 1, 
                            size_scale = 1, space=om2.MSpace.kObject):
    _bnb.betterNormalExecuteOnce(threshold, area_weight, distance_weight, size_scale, space)            
            
            
def betterNormalLiveUpdate(threshold = 0.01, area_weight = 1, distance_weight = 1, 
                            size_scale = 1, space=om2.MSpace.kObject):
    _bnb.betterNormalExcute(threshold, area_weight, distance_weight, size_scale, space)            
    
    
def betterNormal(threshold = 0.01, area_weight = 1, distance_weight = 1, 
                 size_scale = 1, space=om2.MSpace.kObject):
    sel = om2.MGlobal.getActiveSelectionList()
    if sel.length() > 0:
        for i in range(sel.length()):
            shape_path, comp = sel.getComponent(i)
            betterNormalNoSelection(shape_path, comp, threshold, area_weight, distance_weight, size_scale, space)
          

_bnb = BetterNormalBackend()