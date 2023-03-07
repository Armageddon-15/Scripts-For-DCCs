import pymel.core as pmc
import pymel.core.nodetypes as nt
import pymel.core.datatypes as dt

def bb(w=nt.Transform()):
    return w.child()


print(bb(pmc.ls(sl=True, type="transform")[0]))
