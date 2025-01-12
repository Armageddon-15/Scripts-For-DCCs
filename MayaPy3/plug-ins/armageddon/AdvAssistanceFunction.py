from .core import SelectionUtil as SelecUtils
from .core import ObjectTransformation as ObjTrans

import pymel.core.nodetypes as pmnt


def findControlOrInbetween(obj):
    children = ObjTrans.getTransformChildren(obj, False)
    if len(children) == 0:
        return None, False
    for child in children:
        # print(child)
        if str(child).startswith("InbetweenTarget"):
            return obj, True
        shape = ObjTrans.getTransformShapes(child)
        if len(shape)>0:
            if type(shape[0]) is pmnt.NurbsCurve:
                return child, False
        node, is_inbetween = findControlOrInbetween(children)
        if node is not None:
            return node, is_inbetween
    return None, False

def findInbetweenControls(inbetween_target: pmnt.Transform, find_inbetween: bool):
    vis = inbetween_target.inbetweenVis.get()
    vis = find_inbetween and vis
    outputs = inbetween_target.inbetweenVis.outputs()

    # print(inbetween_target, outputs)
    node = outputs[0]
    while node in outputs:
        node, is_inbetween = findControlOrInbetween(node)
        # print(node)
    controller_list = []
    is_final = True
    if node is not None:
        controller_list = [node]
        is_final = False
    if vis:
        controller_list = outputs + controller_list
    return controller_list, is_final


def selectControls(obj, find_inbetween: bool):
    node = obj
    is_inbetween = False
    sel_list = []
    while node is not None:
        if is_inbetween:
            inbetween_nodes, is_final = findInbetweenControls(node, find_inbetween)
            sel_list.extend(inbetween_nodes)
            if is_final:
                break
            else:
                node = inbetween_nodes[0]
        else:
            sel_list.append(node)
        node, is_inbetween = findControlOrInbetween(node)

        # print("\n")
    return sel_list

def selectAllChildrenControls(find_inbetween: bool):
    sel = SelecUtils.orderedSelect()
    sel_list = []
    for o in sel:
        sel_list.extend(selectControls(o, find_inbetween))

    SelecUtils.select(sel_list)


def copyAndConstrain():
    pass