import pymel.core as core
import pymel.core.datatypes as pmdt
import pymel.core.nodetypes as pmnt

import MayaWarning

def copyNode(node):
    try: 
        new_node = core.duplicate(node)[0]
    except Exception as e:
        print(e)
        MayaWarning.warning("instead of duplicate, try to build from stretch")
        new_node = type(node)()
        new_attrs = new_node.listAttr()
        attrs = node.listAttr()
        for j in range(len(new_attrs)):
            try:
                new_attrs[j].set(attrs[j])
            except Exception as ex:
                # print(ex)
                pass
    return new_node