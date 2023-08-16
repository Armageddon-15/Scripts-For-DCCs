import maya.api.OpenMaya as om2

def maya_useNewAPI():
    """
    Tell Maya use open maya 2
    """
    pass


def warning(info):
    om2.MGlobal.displayWarning(info)