import pymel.core as core
import pymel.core.datatypes as pmdt
import pymel.core.nodetypes as pmnt


AXIS_VECTOR_DICT = {"pivot_x": pmdt.Vector([1,0,0]), "pivot_y": pmdt.Vector([0,1,0]), "pivot_z": pmdt.Vector([0,0,1])}


def getSeparateComponentFromSelection(sel, the_type):
    final_list = []
    for obj in sel:
        if type(obj) is the_type:
            for component in obj:
                final_list.append(component)
    return final_list


def getVertexFromSelection(selection):
    return getSeparateComponentFromSelection(selection, core.MeshVertex)


def getFaceFromSelection(selection):
    return getSeparateComponentFromSelection(selection, core.MeshFace)


def getEdgeFromSelection(selection):
    return getSeparateComponentFromSelection(selection, core.MeshEdge)


def getEdgePoints(edge, space="world"):
    vert = []
    if type(edge) is core.MeshEdge:
        vert.append(edge.getPoint(0, space))
        vert.append(edge.getPoint(1, space))
    return vert

def getShapeFromComponent(comp):
    return comp.__str__().split(".")[0]


def getFacePosition(face, space="world"):
    position = pmdt.Vector()
    if type(face) is core.MeshFace:
        vertex_pos_list = face.getPoints(space=space)
        i = 0
        for pos in vertex_pos_list:
            position += pmdt.Vector(pos)
            i += 1
        position /= i
        
    return position


def getEdgeLoopFromEdge(edge):
    if type(edge) is core.MeshEdge:
        edge_loop = core.polySelect(edge, edgeLoopOrBorder=edge.index(), q=True)
        return edge_loop
    

def pointsAlignLineSeparate(start_pos, end_pos, points, max_trace_distance=10000, space="world"):
    normalized_dir = pmdt.normal(end_pos - start_pos)
    with core.UndoChunk("points align line"):
        for point in points:
            dir = point.getPosition(space=space) - start_pos
            project_length = pmdt.dot(dir, normalized_dir)
            project_length = project_length if abs(project_length) < max_trace_distance else 0
            new_pos = normalized_dir * project_length + start_pos
            point.setPosition(new_pos, space=space)


def pointsAlignLine(points, max_trace_distance=10000, space="world"):
    if len(points) > 2:
        start_pos = points[0].getPosition(space=space)
        end_pos = points[1].getPosition(space=space)
        rest_points = points[2:]
        pointsAlignLineSeparate(start_pos, end_pos, rest_points, max_trace_distance, space)
        

def pointsAlignSurfaceSeparate(face_pos, face_normal, points, align_dir=None, max_trace_distance=10000, space="world"):
    
    def rayIntersectPlane(ray_origin, ray_dir, plane_position, plane_normal):
        length = -pmdt.dot(ray_origin -  plane_position, plane_normal) / pmdt.dot(ray_dir, plane_normal)
        length = length if abs(length) < max_trace_distance else 0
        return ray_origin + ray_dir * length      
    
    with core.UndoChunk("points align surface"):
        for vertex in points:
            position = vertex.getPosition(space=space)
            if type(align_dir) is pmdt.Vector or type(align_dir) is pmdt.Point:
                new_pos = rayIntersectPlane(pmdt.Vector(position), pmdt.Vector(align_dir).normal(),
                                            pmdt.Vector(face_pos), face_normal)
            elif align_dir == "normal":
                new_pos = rayIntersectPlane(pmdt.Vector(position), vertex.getNormal(space),
                                            pmdt.Vector(face_pos), face_normal)

            else:
                project_length = pmdt.dot(face_normal, position - face_pos)
                project_length = project_length if project_length < max_trace_distance else 0
                new_pos = position - face_normal * project_length
                if align_dir != "closest":
                    print("type dir is incorrect:", align_dir, type(align_dir))
            vertex.setPosition(new_pos, space=space)    
            

def pointsAlignPointsSurface(points, align_dir=None, max_trace_distance=10000, space="world"):
    if len(points) > 3:
        surface_points = points[:3]
        rest_points = points[3:]        
        pos0 = surface_points[0].getPosition(space=space)
        pos1 = surface_points[1].getPosition(space=space)
        pos2 = surface_points[2].getPosition(space=space)
        
        face_normal = pmdt.normal(pmdt.cross(pos1 - pos0, pos2 - pos0))
        pos = pmdt.Vector(pos0 + pos1 + pos2)/3
        pointsAlignSurfaceSeparate(pos, face_normal, rest_points, align_dir, max_trace_distance, space)
        

def pointsAlignFaceSurface(face, points, align_dir=None, max_trace_distance=10000, space="world"):
    face_pos = getFacePosition(face, space=space)
    face_normal = face.getNormal(space=space)
    pointsAlignSurfaceSeparate(face_pos, face_normal, points, align_dir, max_trace_distance, space)
    
    
def getSortedBordersFromBoarderEdges(border_edges):
    name = border_edges[0].__str__().split(".")[0]
    used_edge_indices = []
    final_edges = []
    
    for edge in border_edges:
        if edge.index() in used_edge_indices:
            continue
        
        edge_loop = getEdgeLoopFromEdge(edge)
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
            separate_edges.extend(getSeparateComponentFromSelection(edges, core.MeshEdge))
            
        border_loops = getSortedBordersFromBoarderEdges(separate_edges)
        return border_loops