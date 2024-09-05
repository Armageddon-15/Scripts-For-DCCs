import pymel.core as core
import pymel.core.nodetypes as pmnt
import pymel.core.datatypes as pmdt 


def rotateVector(dir, dest_dir):
    rotate_axis = pmdt.normal(pmdt.cross(dir, dest_dir))
    rotate_angle = pmdt.acos(pmdt.dot(dir, dest_dir))
    return pmdt.Quaternion(rotate_angle, rotate_axis)


def quaternionToDegreeEulerVector(q):
    return q.asEulerRotation().asVector() * (180/pmdt.pi)