
from .Translate import TranslatorManager
from .GUI import Utils as GuiUtils

from . import NamingFunction

from .GUI.MayaMainWindow import setWidgetAsMayaMainWindow

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


PRIORITY = 4
WIDGET_TITLE_NAME = "Naming"
WIDGET_OBJECT_NAME = "Naming"

class Naming(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        if parent is None:
            setWidgetAsMayaMainWindow(self, WIDGET_TITLE_NAME, WIDGET_OBJECT_NAME)

        self.chain_rename_check = GuiUtils.addWidget(self, QCheckBox)
        TranslatorManager.getTranslator().addTranslate(self.chain_rename_check.setText, "start from 1")
        TranslatorManager.getTranslator().addTranslate(self.chain_rename_check.setToolTip, "N_N_CRC_Tip")
        self.chain_rename_check.setChecked(True)

        self.chain_rename_button = GuiUtils.addButton(self)
        TranslatorManager.getTranslator().addTranslate(self.chain_rename_button.setText, "Add Serial Number Suffix")
        self.chain_rename_button.clicked.connect(self.chainRename)


        self.vbox = QVBoxLayout(self)
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.setSpacing(5)
        self.vbox.addWidget(self.chain_rename_check)
        self.vbox.addWidget(self.chain_rename_button)


    def chainRename(self):
        NamingFunction.chainRename(int(self.chain_rename_check.isChecked()))



def createWidget(obj):
    return Naming(obj)


def show():
    print("\n==== Start", WIDGET_TITLE_NAME, "=====\n")
    ui = Naming()
    ui.show()
    return ui
