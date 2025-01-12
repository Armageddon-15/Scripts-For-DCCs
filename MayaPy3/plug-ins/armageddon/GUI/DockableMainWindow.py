from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from .MayaMainWindow import *
from PySide2.QtWidgets import *


class DockableMainWindow(MayaQWidgetDockableMixin, QMainWindow):
    def __init__(self, widget_type, widget_title_name, widget_object_name, *args, **kwargs):
        super(DockableMainWindow, self).__init__(getMayaMainWindow(), *args, **kwargs)

        setWidgetName(self, widget_title_name, widget_object_name)
        self.central_widget = widget_type(self)
        self.setCentralWidget(self.central_widget)

