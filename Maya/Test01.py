import armageddon.core.SelectionUtil as ac_sutil
import armageddon.core.ObjectTransformation as ac_obj_trans
import armageddon.core.Utils as ac_util
import armageddon.core.Component as ac_component

import pymel.core as core
import pymel.core.nodetypes as pmnt
import pymel.core.datatypes as pmdt 


pivot_rotate = core.manipPivot(q=True, o=True)[0]
pivot_rotate = pmdt.EulerRotation(pivot_rotate, unit="degrees")
print(pivot_rotate)
y_axis = pmdt.Vector([0,1,0])
new_y_axis = y_axis.rotateBy(pivot_rotate)    
new_y_axis.normalize()
print(new_y_axis.normal())
    
sel = ac_sutil.orderedSeclect()
print(sel)
sel = ac_sutil.orderedSeclect()
faces = ac_component.getFaceFromSelection(sel)
print(ac_component.getFacePosition(faces[0]))

vertices = ac_component.getVertexFromSelection(sel)
space = "world"
for v in vertices:
    print(v.getNormal(space="world"))

ac_component.pointsAlignSurface(vertices, new_y_axis, space)


import armageddon.Modeling as arm
arm.show()