import pymel.core as core
import pymel.core.datatypes as pmdt


def checkedSelect(*args, **kwargs):
    list_select = []
    if core.ls(sl = True) != []:
        list_select = core.ls(*args, **kwargs)
        return list_select
    else:
        return []
    
    
def orderedSeclect(*args, **kwargs):
    if core.selectPref(tso=True, q=True) == 0:
        core.selectPref(trackSelectionOrder=True)
    return checkedSelect(orderedSelection=True, *args, **kwargs)


def getComponetShapes(com):
    return core.ls(com, objectsOnly=True)


def getShapeTransforms(shape):
    return core.listRelatives(shape, parent=True)


def getComponetsTransforms(cs):
    c = uniqueList(getComponetShapes(cs))
    return getShapeTransforms(c)


def uniqueList(l):
    search_set = set()
    new_list = []
    for item in l:
        if item not in search_set:
            new_list.append(item)
            search_set.add(item)
            
    return new_list
    

def getSelectVerticesInOredered():
    selection = orderedSeclect()
    vertex_list = []
    for item in selection:
        if type(item) is core.MeshVertex:
            for vertex in item:
                vertex_list.append(vertex)
    return vertex_list
        

def pointsAlignLine(pos0, pos1, points, space="object"):
    normalized_dir = pmdt.normal(pos1 - pos0)
    
    for point in points:
        dir = point.getPosition(space=space) - pos0
        project_length = pmdt.dot(dir, normalized_dir)
        new_pos = normalized_dir * project_length + pos0
        if space == "world":
            new_pos = point.translateBy(new_pos, space="object")
        point.setPosition(new_pos)
        

def selectVerticesAlignLine(space="object"):
    vertices = getSelectVerticesInOredered()

    if len(vertices) >=3:
        pos0 = vertices[0].getPosition(space=space)
        pos1 = vertices[1].getPosition(space=space)
        other_points = vertices[2:]
        pointsAlignLine(pos0, pos1, other_points)


vertices = getSelectVerticesInOredered()
t = getComponetsTransforms(vertices)

if len(vertices) >=4:
    pos0 = vertices[0].getPosition()
    pos1 = vertices[1].getPosition()
    pos2 = vertices[2].getPosition()
    for vertex in vertices:
        print(vertex.getPosition())
    
    face_normal = pmdt.normal(pmdt.cross(pos1 - pos0, pos2 - pos0))
    
    points = vertices[3:]
    for vertex in points:
        position = vertex.getPosition()
        normal_project_length = pmdt.dot(face_normal, vertex.getPosition() - pos0)
        new_pos = position - face_normal * normal_project_length
        vertex.setPosition(new_pos)