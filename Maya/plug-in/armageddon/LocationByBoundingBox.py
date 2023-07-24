# -*- coding: UTF-8 -*-

import LocationByBoundingBoxFunction as Func

import pymel.core as core

from maya import OpenMayaUI as omui 

from GUI import RadioGroup

from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance 


mayaMainWindowPtr = omui.MQtUtil.mainWindow() 
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget) 


WIDGET_OBJECT_NAME = u"location_by_bbox"
WIDGET_TITLE_NAME = u"劲爆大象部落 0.0.1"

class LocationByBoundingBox(QWidget):
    def __init__(self, *args, **kwargs):
        super(LocationByBoundingBox, self).__init__(*args, **kwargs)
        
        try:
            core.deleteUI(WIDGET_OBJECT_NAME)
        except Exception as e:
            print(e)
            
        self.setObjectName(WIDGET_OBJECT_NAME)
        self.setParent(mayaMainWindow)
        self.setWindowFlags(Qt.Window)
        
        self.setWindowTitle(WIDGET_TITLE_NAME)
        self.setGeometry(50, 50, 250, 150)
        
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)
        self.vbox.setAlignment(Qt.AlignTop)
        
        self.axis_radio_group = []
        self.addRadioBtn()
        
        self.pivot_btn = QPushButton(self)
        self.pivot_btn.setText("Set Pivot")
        self.pivot_btn.setToolTip("Transforms types only")
        # self.pivot_btn.clicked.connect(self.setPivotPosition)
        
        self.bbox_btn = QPushButton(self)
        self.bbox_btn.setText("To World Center")
        self.bbox_btn.setToolTip("Transforms types only")
        # self.bbox_btn.clicked.connect(self.setPosition)
        
        self.group_bbox_btn = QPushButton(self)
        self.group_bbox_btn.setText("To World Center Group")
        # self.group_bbox_btn.clicked.connect(self.setGroupToWorldCenter)
        
        self.vbox.addWidget(self.pivot_btn)
        self.vbox.addWidget(self.bbox_btn)
        self.vbox.addWidget(self.group_bbox_btn)
        
        
    def addRadioBtn(self):
        x_radio_group = RadioGroup.RadioGroup("X-aixs:", self)
        y_radio_group = RadioGroup.RadioGroup("Y-aixs:", self)
        z_radio_group = RadioGroup.RadioGroup("Z-aixs:", self)
        
        x_radio_group.addRadioBtn("Min")
        x_radio_group.addRadioBtn("Mid")
        x_radio_group.addRadioBtn("Max")
        x_radio_group.addRadioBtn("Ignore")
        x_radio_group.layoutWidget()
        self.vbox.addWidget(x_radio_group)
        
        y_radio_group.addRadioBtn("Min")
        y_radio_group.addRadioBtn("Mid")
        y_radio_group.addRadioBtn("Max")
        y_radio_group.addRadioBtn("Ignore")        
        y_radio_group.layoutWidget()
        self.vbox.addWidget(y_radio_group)
        
        z_radio_group.addRadioBtn("Min")
        z_radio_group.addRadioBtn("Mid")
        z_radio_group.addRadioBtn("Max")
        z_radio_group.addRadioBtn("Ignore")         
        z_radio_group.layoutWidget()
        self.vbox.addWidget(z_radio_group)
        
        self.axis_radio_group = [x_radio_group, y_radio_group, z_radio_group]
        
        



def show():
    print("\n====Start UI1=====\n")
    ui = LocationByBoundingBox()
    ui.show()
    return ui
    
if __name__ == '__main__':
    show()
