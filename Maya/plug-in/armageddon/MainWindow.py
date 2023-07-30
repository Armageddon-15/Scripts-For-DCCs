import Parameters

import LocationByBoundingBox, Modeling

from GUI import CollapsibleWidget

from GUI.MayaMainWindow import setWidgetAsMayaMainWindow

from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *


class MainWindow(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        if parent is None:
            setWidgetAsMayaMainWindow(self, Parameters.MAIN_WIDGET_TITLE_NAME, Parameters.MAIN_WIDGET_OBJECT_NAME)
        
        self.location_widget = LocationByBoundingBox.LocationByBoundingBox(self)
        self.location_collapsible_header = CollapsibleWidget.CollapsibleHeader(self, LocationByBoundingBox.WIDGET_TITLE_NAME,
                                                                               self.location_widget)
        
        self.modeling_widget = Modeling.AlignmentWidget(self)
        self.modeling_collapsible_header = CollapsibleWidget.CollapsibleHeader(self, Modeling.WIDGET_TITLE_NAME,
                                                                               self.modeling_widget)
        
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(1,1,1,1)
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.addWidget(self.location_collapsible_header)
        self.vbox.addWidget(self.modeling_collapsible_header)
        
        
        
def show():
    print("\n====Start Armageddon Main Window=====\n")
    ui = MainWindow()
    ui.show()
    return ui
    
if __name__ == '__main__':
    show()