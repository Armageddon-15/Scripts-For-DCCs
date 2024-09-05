import maya.api.OpenMaya as om2
import Utils


def vertexIndexToSelection(shape_path, vertices):
    sel = om2.MSelectionList()
    for vertex in vertices:
        p = ".vtx[%s]"%vertex
        sel.add(str(shape_path) + p)

    om2.MGlobal.setActiveSelectionList(sel)
    return sel


def getVertIterFromSelection(dag, component):
    if component.apiType() == om2.MFn.kMeshEdgeComponent:
        vertices = []
        for edge in om2.MItMeshEdge(dag, component):
            vertices.append(edge.vertexId(0))
            vertices.append(edge.vertexId(1))
        vertices = Utils.uniqueList(vertices)
        d, c = vertexIndexToSelection(dag, vertices).getComponent(0)
        return om2.MItMeshVertex(d, c)
    
    elif component.apiType() == om2.MFn.kMeshPolygonComponent:
        vertices = []
        for face in om2.MItMeshPolygon(dag, component):
            vert = face.getVertices()
            for v in vert:
                vertices.append(v)
        vertices = Utils.uniqueList(vertices)
        d, c = vertexIndexToSelection(dag, vertices).getComponent(0)
        return om2.MItMeshVertex(d, c)
    
    return om2.MItMeshVertex(dag, component)         


def convertSelectionToVertexSelection():
    sel=om2.MGlobal.getActiveSelectionList()
    new_sel = om2.MSelectionList()
    for i in range(sel.length()):
        dag, component = sel.getComponent(i)
        if component.apiType() == om2.MFn.kMeshEdgeComponent:
            vertices = []
            for edge in om2.MItMeshEdge(dag, component):
                vertices.append(edge.vertexId(0))
                vertices.append(edge.vertexId(1))
            vertices = Utils.uniqueList(vertices)
            d, c = vertexIndexToSelection(dag, vertices).getComponent(0) 
            new_sel.add((d,c))
        elif component.apiType() == om2.MFn.kMeshPolygonComponent:
            vertices = []
            for face in om2.MItMeshPolygon(dag, component):
                vert = face.getVertices()
                for v in vert:
                    vertices.append(v)
            vertices = Utils.uniqueList(vertices)
            d, c = vertexIndexToSelection(dag, vertices).getComponent(0)    
            new_sel.add((d,c))
        else:
            new_sel.add((dag, component))
    om2.MGlobal.setActiveSelectionList(new_sel)            
    return new_sel