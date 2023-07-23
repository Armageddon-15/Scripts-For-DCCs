import Utils

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


def shapeSelect(com):
    """this one is not for viewport selection

    Args:
        com (nt.Transform): transform

    Returns:
        nt.Shape: shapes in transform
    """
    return core.ls(com, objectsOnly=True)
