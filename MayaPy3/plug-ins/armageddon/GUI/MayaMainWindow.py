# -*- coding: UTF-8 -*-

from maya import OpenMayaUI as omui 

from shiboken2 import wrapInstance 

import pymel.core as core

from PySide2.QtWidgets import QWidget
from PySide2.QtCore import Qt
    
    
def getMayaMainWindow():
    maya_main_window_ptr = omui.MQtUtil.mainWindow() 
    maya_main_window = wrapInstance(int(maya_main_window_ptr), QWidget)
    return maya_main_window


def deleteUiObject(object_name):
    if object_name is not None:
        try:
            core.deleteUI(object_name)
        except Exception as e:
            # print(e)
            pass
        try:
            core.deleteUI(object_name+"WorkspaceControl")
        except Exception as e:
            pass
    
    

def setWidgetAsMayaMainWindow(widget, title_name="DefaultTitle", object_name=None):

    deleteUiObject(object_name)
        
    if object_name is not None:
        try:
            widget.setObjectName(object_name)
        except BaseException as e:
            pass
            
    main_window = getMayaMainWindow()
    widget.setParent(main_window)
    widget.setWindowFlags(Qt.Window)
    
    widget.setWindowTitle(title_name)
    
    
def setWidgetName(widget, title_name="DefaultTitle", object_name=None):
        
    deleteUiObject(object_name)
        
    if object_name is not None:
        try:
            widget.setObjectName(object_name)
        except BaseException as e:
            pass
            
    widget.setWindowTitle(title_name)

    
    
class MayaMainWidget(QWidget):
    def __init__(self, parent=None, title_name="DefaultTitle", object_name=None, *args, **kwargs):
        super(MayaMainWidget, self).__init__(parent=None, *args, **kwargs)
        if parent is None:
            setWidgetAsMayaMainWindow(self, title_name, object_name)
        
        self.main = parent