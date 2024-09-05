import pymel.core as core
import pymel.core.datatypes as pmdt
import pymel.core.nodetypes as pmnt


def uniqueList(l):
    search_set = set()
    new_list = []
    for item in l:
        if item not in search_set:
            new_list.append(item)
            search_set.add(item)
            
    return new_list


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


def getCertainTypeFromList(sel, the_type):
    final_list = []
    for obj in sel:
        if type(obj) is the_type:
            final_list.append(obj)
    return final_list


def getTransformChildren(transform, transform_only=True):
    children = core.listRelatives(transform, children=True)
    if not transform_only:
        return children        

    final_list = []
    for child in children:
        if type(child) is pmnt.Transform:
            final_list.append(child)
    return final_list


def getTransformParent(transform):
    return core.listRelatives(transform, parent=True)


def makeConstraintJoint(joint):
    if type(joint) is not pmnt.Joint:
        return
    children = joint.getChildren()
    joint_name = str(joint)+"_CJ"
    for c in children:
        if str(c) == joint_name:
            return c
    core.select(d=True)
    constraint_joint = core.joint(p=(0, 0, 0), n=joint_name)
    core.parent(constraint_joint, joint, r=True)
    return constraint_joint


def createControllerHierachy(ctrl, constraint_joint):
    sys_root_name = "Group|MotionSystem|CustomSystem"
    sys_root = core.ls(sys_root_name)
    if len(sys_root) != 1:
        return
    sys_root = sys_root[0]
    
    joint_name = str(constraint_joint)
    root_name = "ParentConstraintTo" + joint_name
    
    root = core.ls(sys_root_name + "|" + root_name)
    if len(root) == 0:
        root_pos = constraint_joint.getTranslation(space="world")
        root = core.group(em=True, name=root_name)
        root.setTranslation(root_pos, space="world")
        core.parentConstraint(constraint_joint, root, mo=True)
        core.parent(root, sys_root)
    else:
        root = root[0]

    ctrl_name = str(ctrl)
    parent = getTransformParent(ctrl)
    parent_name = "Offset" + ctrl_name
    core.rename(parent, parent_name)
    core.parent(parent, root)
    
    sdk_name = "SDK" + ctrl_name
    sdk = core.group(em=True, name=sdk_name, parent=parent_name)
    # core.parent(sdk_name, parent, r=True)
    core.parent(ctrl, sdk)
    return sdk


def findControlJoint(ctrl):
    ll = core.listConnections(ctrl, type=pmnt.Constraint)
    if len(ll) == 0:
        return
    cs = uniqueList(ll)[0]
    return cs.getParent()

def constraintJoint(controller, sdk, joint): 
    name = str(sdk)
    mul_name = name + "_RScaeleMPD"
    node = core.createNode("multiplyDivide", n=mul_name)
    node.output.connect(joint.scale)
    sdk.scale.connect(node.input1)
    controller.scale.connect(node.input2)


def main():
    selections = orderedSeclect()
    joint = getCertainTypeFromList(selections, pmnt.Joint)[0]
    if joint is None:
        return
    selections.remove(joint)
    controllers = selections
    print controllers
    cj = makeConstraintJoint(joint)
    for trans in controllers:
        control_joint = findControlJoint(trans)
        sdk = createControllerHierachy(trans, cj)
        constraintJoint(trans, sdk, control_joint)

    
main()
