from maya import OpenMayaUI as omui 
from shiboken2 import wrapInstance 

import pymel.core as core

from PySide2.QtWidgets import QWidget
from PySide2.QtCore import Qt


def setWidgetAsMayaMainWindow(widget, title_name="DefaultTitle", object_name=None):
    
    try:
        core.deleteUI(object_name)
    except Exception as e:
        print(e)
        
    widget.setObjectName(object_name)
    
    MAYA_MAIN_WINDOW_PTR = omui.MQtUtil.mainWindow() 
    MAYA_MAIN_WINDOW = wrapInstance(long(MAYA_MAIN_WINDOW_PTR), QWidget) 
    widget.setParent(MAYA_MAIN_WINDOW)
    widget.setWindowFlags(Qt.Window)
    
    widget.setWindowTitle(title_name)