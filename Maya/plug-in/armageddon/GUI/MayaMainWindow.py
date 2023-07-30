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
        
    if object_name is not None:
        widget.setObjectName(object_name)
    
    MAYA_MAIN_WINDOW_PTR = omui.MQtUtil.mainWindow() 
    MAYA_MAIN_WINDOW = wrapInstance(long(MAYA_MAIN_WINDOW_PTR), QWidget) 
    widget.setParent(MAYA_MAIN_WINDOW)
    widget.setWindowFlags(Qt.Window)
    
    widget.setWindowTitle(title_name)
    
    
class MayaMainWidget(QWidget):
    def __init__(self, parent=None, title_name="DefaultTitle", object_name=None, *args, **kwargs):
        super(MayaMainWidget, self).__init__(parent=None, *args, **kwargs)
        if parent is None:
            setWidgetAsMayaMainWindow(self, title_name, object_name)
        
        self.main = parent