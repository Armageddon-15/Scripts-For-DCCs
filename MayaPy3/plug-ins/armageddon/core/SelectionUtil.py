from . import Utils

import pymel.core as core
import pymel.core.datatypes as pmdt
import pymel.core.nodetypes as pmnt


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


def getCertainTypeFromSelection(sel, the_type):
    final_list = []
    for obj in sel:
        if type(obj) is the_type:
            for component in obj:
                final_list.append(component)
    return final_list


def shapeSelect(com):
    """this one is not for viewport selection

    Args:
        com (nt.Transform): transform

    Returns:
        nt.Shape: shapes in transform
    """
    return core.ls(com, objectsOnly=True)


def keepTopMostSelectedTransform(selection):
    selected_top_parent_set = set()

    for obj in selection:
        if type(obj) is pmnt.Transform:
            parents = obj.getAllParents()
            if len(parents) > 0:
                all_not_in_sel = True
                for p in reversed(parents):
                    if p in selection:
                        all_not_in_sel = False
                        selected_top_parent_set.add(p)
                        break
                if all_not_in_sel:
                    selected_top_parent_set.add(obj)
            else:
                selected_top_parent_set.add(obj)
    return list(selected_top_parent_set)


def select(sel):
    name_list = []
    if type(sel) is list:
        for obj in sel:
            name_list.append(obj.__melobject__())
    else:
        name_list = [sel]
    core.select(name_list)