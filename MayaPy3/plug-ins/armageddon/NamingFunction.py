from .core import ObjectTransformation as ObjTrans
from .core import SelectionUtil as SelectUtils

import pymel.core as core


def chainRename(start_index = 1):
    sel = SelectUtils.orderedSelect()
    for obj in sel:
        children = ObjTrans.getTransformAllChildren(obj, False)

        name_prefix = str(obj)
        print(name_prefix)
        i = start_index
        for child in children:
            core.rename(child, name_prefix + str(i))
            i += 1