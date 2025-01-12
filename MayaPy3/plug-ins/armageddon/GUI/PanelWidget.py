from . import Utils as GuiUtils

from .MayaMainWindow import *
from . import DockableMainWindow

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class PanelWidget(QWidget):
    def __init__(self, parent=None, widget_title_name="", widget_object_name="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.widget_title_name = widget_title_name
        self.widget_object_name = widget_object_name
        if parent is None:
            setWidgetAsMayaMainWindow(self, widget_title_name, widget_object_name)

    def showWindow(self):
        print("\n==== Start", self.widget_title_name, "=====\n")
        ui = DockableMainWindow.DockableMainWindow(type(self), self.widget_title_name, self.widget_object_name)
        ui.show(dockable=True)
        return ui

