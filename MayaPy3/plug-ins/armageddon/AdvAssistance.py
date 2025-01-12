from . import AdvAssistanceFunction as AdvFunc

from .Translate import TranslatorManager
from .GUI import Utils as GuiUtils

from .GUI import PanelWidget

from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *

PRIORITY = 5
WIDGET_TITLE_NAME = "Adv Assistance"
WIDGET_OBJECT_NAME = "advance_skeleton_assistance"


class AdvAssistance(PanelWidget.PanelWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(AdvAssistance, self).__init__(parent, WIDGET_TITLE_NAME, WIDGET_OBJECT_NAME, *args, **kwargs)

        self.control_include_inbetween = GuiUtils.addWidget(self, QCheckBox)
        TranslatorManager.getTranslator().addTranslate(self.control_include_inbetween.setText, "Include Inbetween")
        self.control_include_inbetween.setChecked(True)
        self.btn = GuiUtils.addButton(self)
        TranslatorManager.getTranslator().addTranslate(self.btn.setText, "Select Children Control")
        self.btn.clicked.connect(self.selectChildrenControls)

        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.control_include_inbetween)
        self.vbox.addWidget(self.btn)


    def selectChildrenControls(self):
        AdvFunc.selectAllChildrenControls(self.control_include_inbetween.isChecked())


def createWidget(obj):
    return AdvAssistance(obj)

def show():
    ui = AdvAssistance()
    ui.showWindow()
    return ui
