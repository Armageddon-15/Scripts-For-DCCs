# -*- coding: UTF-8 -*-

from .GUI import Separator, WidgetWithHeader, WidgetWithName
from .GUI import Utils as GuiUtils

from . import BakePreparationFunction

from .GUI.MayaMainWindow import setWidgetAsMayaMainWindow

from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *

PRIORITY = 0
WIDGET_TITLE_NAME = "Bake Preparation"
WIDGET_OBJECT_NAME = "bake_preparation"


class BakePreparation(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(BakePreparation,self).__init__(parent, *args, **kwargs)
        
        if parent is None:
            setWidgetAsMayaMainWindow(self, WIDGET_TITLE_NAME, WIDGET_OBJECT_NAME)
            
            
        self.unique_material_btn = GuiUtils.addButton(self, "Unique Selected Material",
                                                      "每个选到的transform，都会根据自己的名称\n"\
                                                      "和材质类型重新指定材质\n"\
                                                      "建议不要用默认材质lambert1，因为这个复制起来会比较慢")
        
        self.unique_material_btn.clicked.connect(self.clickUniqueMaterialBtn)
        
        self.include_children_cbox = GuiUtils.addWidget(self, QCheckBox, "Include Children")
        
        self.include_children_cbox.setChecked(True)
        self.include_material_connection = GuiUtils.addWidget(self, QCheckBox, "Include Material Connection",
                                                              "复制材质后面链接的节点，目前不支持")
        self.include_material_connection.setCheckable(False)
        
        self.check_frame = QFrame(self)
        self.check_hbox = QHBoxLayout(self.check_frame)
        self.check_hbox.addWidget(self.include_children_cbox)
        self.check_hbox.addWidget(self.include_material_connection)
        
        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.unique_material_btn)
        self.vbox.addWidget(self.check_frame)
        
    def clickUniqueMaterialBtn(self):
        print("hi from h")
        BakePreparationFunction.uniqueEachMaterial(self.include_children_cbox.isChecked())
        
        

def createWidget(obj):
    return BakePreparation(obj)


def show():
    print("\n==== Start", WIDGET_TITLE_NAME, "=====\n")
    ui = BakePreparation()
    ui.show()
    return ui