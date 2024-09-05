# -*- coding: UTF-8 -*-
import sys

for path in sys.path:
    print(path)
import Parameters

import LocationByBoundingBox, Modeling, PivotAlignment, BakePreparation
from GUI import CollapsibleWidget
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from GUI.MayaMainWindow import *
from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *

if not "main_ui" in globals():
    main_ui = None


class ItemWidget(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(ItemWidget, self).__init__(parent, *args, **kwargs)
        if parent is None:
            setWidgetAsMayaMainWindow(self, Parameters.MAIN_WIDGET_TITLE_NAME, Parameters.MAIN_WIDGET_OBJECT_NAME) 
            
        # 0 - scroll
        # 1 - tab
        self.current_layout = 0
        
        self.location_widget = LocationByBoundingBox.LocationByBoundingBox(self)
        self.location_collapsible_header = CollapsibleWidget.CollapsibleHeader(self, LocationByBoundingBox.WIDGET_TITLE_NAME,
                                                                               self.location_widget)
        
        self.modeling_widget = Modeling.Modeling(self)
        self.modeling_collapsible_header = CollapsibleWidget.CollapsibleHeader(self, Modeling.WIDGET_TITLE_NAME,
                                                                               self.modeling_widget)
                
        self.pivot_align_widget = PivotAlignment.PivotAligment(self)
        self.pivot_align_collapsible_header = CollapsibleWidget.CollapsibleHeader(self, PivotAlignment.WIDGET_TITLE_NAME,
                                                                               self.pivot_align_widget)
                
        self.bake_preparation_widget = BakePreparation.BakePreparation(self)
        self.bake_preparation_collapsible_header = CollapsibleWidget.CollapsibleHeader(self, BakePreparation.WIDGET_TITLE_NAME,
                                                                               self.bake_preparation_widget)        
        self.panel_list = [self.location_collapsible_header, self.modeling_collapsible_header, 
                           self.pivot_align_collapsible_header, self.bake_preparation_collapsible_header]

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setMovable(True)
        self.tab_widget.hide()
        
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.horizontalScrollBar().setEnabled(False)
        self.scroll_area.horizontalScrollBar().hide()        
        self.scroll_area.setFrameStyle(0)
        self.scroll_widget = QWidget(self)
        self.scroll_vbox = QVBoxLayout(self.scroll_widget)
        self.scroll_vbox.setContentsMargins(1,1,1,1)
        self.scroll_vbox.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(1,1,1,1)
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.addWidget(self.scroll_area)
        
        self.switchToScroll()
        # self.vbox.addWidget(self.modeling_collapsible_header)
        
    @staticmethod
    def removeBoxItems(box):
        for i in reversed(range(0, box.count())):
            # box.itemAt(i).widget().hide()
            box.removeWidget(box.itemAt(i).widget())
        
    def switchToTab(self):
        self.removeBoxItems(self.scroll_vbox)
        for panel in self.panel_list:
            self.tab_widget.addTab(panel, panel.getHeaderName())
        
        self.removeBoxItems(self.vbox)
        self.vbox.addWidget(self.tab_widget)
           
        self.tab_widget.show()
        self.scroll_area.hide()
        
        self.current_layout = 1
        
    def switchToScroll(self):
        self.tab_widget.clear()
        
        self.tab_widget.hide()    
        self.scroll_area.show()
        for panel in self.panel_list:
            panel.show()
            self.scroll_vbox.addWidget(panel)
            
        self.removeBoxItems(self.vbox)
        self.vbox.addWidget(self.scroll_area)         
        self.scroll_area.setMinimumWidth(max(self.scroll_area.minimumWidth(), self.scroll_widget.sizeHint().width()+10)) 
        self.current_layout = 0


class MainWindow(MayaQWidgetDockableMixin, QMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        super(MainWindow, self).__init__(parent, *args, **kwargs)
        if parent is None:
            setWidgetAsMayaMainWindow(self, Parameters.MAIN_WIDGET_TITLE_NAME, Parameters.MAIN_WIDGET_OBJECT_NAME)
        else:
            setWidgetName(self, Parameters.MAIN_WIDGET_TITLE_NAME, Parameters.MAIN_WIDGET_OBJECT_NAME)
            

        self.addSettingsMenu()
        
        self.item_widget = ItemWidget(self)
        self.setCentralWidget(self.item_widget)
        
    
    def addSettingsMenu(self):
        settings = self.menuBar().addMenu("Settings")
        switch_action = QAction("Switch Layout", self)
        switch_action.triggered.connect(self.switchLayout)
        settings.addAction(switch_action)
        
        
    def switchLayout(self):
        if self.item_widget.current_layout == 0:
            self.item_widget.switchToTab()
        elif self.item_widget.current_layout == 1:
            self.item_widget.switchToScroll()
        
       
        
def DockableWidgetUIScript():
    global main_ui
    main_ui = MainWindow(getMayaMainWindow())  
    main_ui.show(dockable=True)
    return main_ui
        
        
def show():
    print("\n====Start Armageddon Main Window=====\n")
    ui = DockableWidgetUIScript()
    return ui


def switchToTab():
    main_ui.switchToTab()
    
    
def switchToScroll():
    main_ui.switchToScroll()   
     
    
if __name__ == '__main__':
    show()