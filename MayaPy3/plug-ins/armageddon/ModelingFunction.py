from .core import Utils as Utils
from .core import Component as Component
from .core import SelectionUtil as SelecUtils

import pymel.core as core
import pymel.core.nodetypes as pmnt
import pymel.core.datatypes as pmdt 


def verticesAlignLine(max_trace_distance=10000):
    sel = SelecUtils.orderedSelect()
    vertices = Component.getVertexFromSelection(sel)
    edges = Component.getEdgeFromSelection(sel)
    if len(edges) > 0:
        edge_vert = Component.getEdgePoints(edges[0])
        Component.pointsAlignLineSeparate(edge_vert[0], edge_vert[1], vertices,
                                          max_trace_distance)
    else:
        Component.pointsAlignLine(vertices , max_trace_distance)
    
    
def verticesAlignFace(dir_state="closest", max_trace_distance=10000):
    """
    dir_state is a str, which control how point project to the face
    it can be:
        closest - default option, cheapest way
        normal - use vertex normal, which is just average normal of connected faces
        pivot_x - x axis of current pivot in viewport
        pivot_y - y axis of current pivot in viewport    
        pivot_z - z axis of current pivot in viewport
    
    Besides "closest", others use ray intersect plane method            
    """
    
    if dir_state == "normal":
        align_dir = "normal"
    elif dir_state == "closest":
        align_dir = None
    else:
        pivot_rotate = core.manipPivot(q=True, o=True)[0]
        pivot_rotate = pmdt.EulerRotation(pivot_rotate, unit="degrees")
        print(pivot_rotate)
        pivot_dir = Component.AXIS_VECTOR_DICT[dir_state]
        align_dir = pivot_dir.rotateBy(pivot_rotate)
    
    sel = SelecUtils.orderedSelect()
    vertices = Component.getVertexFromSelection(sel)
    faces = Component.getFaceFromSelection(sel)
    if len(faces) > 0:
        Component.pointsAlignFaceSurface(faces[0], vertices, align_dir, max_trace_distance)
    else:
        Component.pointsAlignPointsSurface(vertices, align_dir, max_trace_distance)
        
    print(vertices, faces)
    
    
def flatFaces(flat_pos="average"):
    pass