# -*- coding: utf-8 -*- 

import maya.cmds as cmd
import sys


reload(sys)
sys.setdefaultencoding('utf-8')


#解决中文问题
def utf_8String(StringT):
    utf_8String = StringT
    utf_8String.encode('utf-8')
    utf_8String = unicode(utf_8String, "utf-8")
    return utf_8String


def checkSelect(*args, **kwargs):
    list_select = []
    if cmd.ls(sl = True) != []:
        list_select = cmd.ls(sl=True, *args, **kwargs)
        return list_select
    else:
        return []


def average2(a, b):
    return (a+b)/2


#坐标回归中心
def centerPivot(obj):
    cmd.xform(obj, centerPivots=True)
    
    
def bottomCenterPivot(obj):
    bbox = cmd.exactWorldBoundingBox(obj)
    p_pos = cmd.getAttr(obj + ".scalePivot")[0]
    b_center = [average2(bbox[0], bbox[3]), bbox[1], average2(bbox[2], bbox[5])]
    cmd.xform(obj, pivots=b_center, worldSpace=True)
    cmd.move(0, 0, 0, obj,rpr=True)
    cmd.makeIdentity(obj, a=True)
    cmd.xform(obj, pivots = p_pos, worldSpace=True)
        

def allParents(obj, p_list=[]):
    parent = cmd.listRelatives(obj, p=True, c=False)
    if parent is not None:
        p_list.append(parent[0], p_list)
        allParents(parent)
        
    return p_list


def exactPath(obj):
    return cmd.listRelatives(obj, c=False, path=True)


def listToParentFullPath(parent_list):
    s = ""
    for name in parent_list:
        s += name + "|"

    s = s[:len(s)-1]


def groupMoveToWorldCenter():
    sel_dict = {}
    ss = checkSelect(l=True)
    m_group = cmd.group(em=True)

    count = "b#"
    for sel in ss:
        n = sel.rfind("|")
        name_list = [sel[:n], sel[n+1:]]
        name = cmd.rename(sel, count)
        sel_dict.update({name: name_list})

        cmd.parent(name, m_group)

    bottomCenterPivot(m_group)

    for key, val in reversed(sel_dict.items()):
        name = "|" + m_group + "|" + key
        name = cmd.rename(name, sel_dict[key][1])
        if sel_dict[key][0] != "":
            cmd.parent(name, sel_dict[key][0])
        else:
            cmd.parent(name, w=True)
        
    cmd.delete(m_group)
    cmd.select(ss)
    
    
def mainGUI():
    window_name = "Armageddon15-Tools"
    window_title = "劲爆大象部落 0.0.1"
    
    if cmd.window(window_name, exists=True):
        cmd.deleteUI(window_name)
    
    cmd.window(window_name, t = window_title )
    cmd.showWindow()
    

mainGUI()

