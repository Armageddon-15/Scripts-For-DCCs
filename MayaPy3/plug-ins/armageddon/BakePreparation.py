# -*- coding: UTF-8 -*-

from .Translate import TranslatorManager
from .GUI import Utils as GuiUtils

from . import BakePreparationFunction

from .GUI.MayaMainWindow import setWidgetAsMayaMainWindow

from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *

PRIORITY = 3
WIDGET_TITLE_NAME = "Bake Preparation"
WIDGET_OBJECT_NAME = "bake_preparation"


class BakePreparation(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(BakePreparation,self).__init__(parent, *args, **kwargs)
        
        if parent is None:
            setWidgetAsMayaMainWindow(self, WIDGET_TITLE_NAME, WIDGET_OBJECT_NAME)

        
        self.include_children_cbox = GuiUtils.addWidget(self, QCheckBox)
        TranslatorManager.getTranslator().addTranslate(self.include_children_cbox.setText, "Include Children")
        
        self.include_children_cbox.setChecked(True)
        self.include_material_connection = GuiUtils.addWidget(self, QCheckBox)
        TranslatorManager.getTranslator().addTranslate(self.include_material_connection.setText, "Include Material Connection")
        TranslatorManager.getTranslator().addTranslate(self.include_material_connection.setToolTip, "BP_BP_IMC_Btn_Tip")
        self.include_material_connection.setCheckable(False)
        
        self.check_frame = QFrame(self)
        self.check_hbox = QHBoxLayout(self.check_frame)
        self.check_hbox.addWidget(self.include_children_cbox)
        self.check_hbox.addWidget(self.include_material_connection)

        self.unique_material_btn = GuiUtils.addButton(self,
                                                      "每个选到的transform，都会根据自己的名称\n"\
                                                      "和材质类型重新指定材质\n"\
                                                      "建议不要用默认材质lambert1，因为这个复制起来会比较慢")
        TranslatorManager.getTranslator().addTranslate(self.unique_material_btn.setText, "Unique Selected Material")
        TranslatorManager.getTranslator().addTranslate(self.unique_material_btn.setToolTip, "bake_preparation_unique_mat_btn")

        self.unique_material_btn.clicked.connect(self.clickUniqueMaterialBtn)
        
        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.check_frame)
        self.vbox.addWidget(self.unique_material_btn)
        
    def clickUniqueMaterialBtn(self):
        BakePreparationFunction.uniqueEachMaterial(self.include_children_cbox.isChecked())
        
        

def createWidget(obj):
    return BakePreparation(obj)


def show():
    print("\n==== Start", WIDGET_TITLE_NAME, "=====\n")
    ui = BakePreparation()
    ui.show()
    return ui