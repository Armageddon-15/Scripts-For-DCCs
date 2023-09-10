import maya.cmds as cmds


s = cmds.fileDialog2(fm=3, caption="Batch Export FBX--Select A Directory", ds=2, ff="-")
print(s)

if s is not None:
    s=s[0]
    sel = cmds.ls(sl=True)
    print(sel)
    
    for o in sel:
        cmds.select(o, add=False)
        cmds.file(s+"/"+o+".fbx", force=True, options="fbx", typ="FBX export", pr=True, es=True)
        
    cmds.select(sel, add=False)