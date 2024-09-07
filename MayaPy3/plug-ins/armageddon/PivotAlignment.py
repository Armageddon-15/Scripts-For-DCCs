# -*- coding: UTF-8 -*-

from .GUI import Separator, WidgetWithHeader, WidgetWithName, VectorVis
from .GUI import Utils as GuiUtils

from . import PivotAlignmentFunction

from .GUI.MayaMainWindow import setWidgetAsMayaMainWindow

from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *

PRIORITY = 0
WIDGET_TITLE_NAME = "Pivot Align Tube"
WIDGET_OBJECT_NAME = "pivot_align_tube"

class PivotAligment(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(PivotAligment, self).__init__(parent, *args, **kwargs)
        
        if parent is None:
            setWidgetAsMayaMainWindow(self, WIDGET_TITLE_NAME, WIDGET_OBJECT_NAME)
            
        self.check_widget = QFrame(self)
        self.check_hbox = QHBoxLayout(self.check_widget)
        self.check_hbox.setContentsMargins(0,0,0,0)
        self.set_trans = GuiUtils.addWidget(self, QCheckBox, "Set Translation")
        self.set_trans.setChecked(True)
        self.set_ori = GuiUtils.addWidget(self, QCheckBox, "Set Orientation")   
        self.set_ori.setChecked(True)
        self.check_hbox.addWidget(self.set_trans)
        self.check_hbox.addWidget(self.set_ori)
        
        self.bake_if_mult = GuiUtils.addWidget(self, QCheckBox, "Bake pivot if more than one", 
                                               "如果选择的tranform大于1就烘焙枢轴，否则结果可能不符合预期")   
        self.bake_if_mult.setChecked(True) 
        
        self.invert_pivot = GuiUtils.addButton(self, "Invert Pivot",
                                               "旋转轴将采用第二级枢轴")  
        self.invert_pivot.clicked.connect(self.invertPivot)
             
        self.searching_method = WidgetWithName.ComboBox(self, "Searching Method:")
        self.searching_method.addItem("Max", "max")
        self.searching_method.addItem("Min", "min")
        self.searching_method.addItem("Select Loop", "select_loop")
        self.searching_method.addItem("Not For Transform", "ignore")
        
        self.pivot_align_axis = WidgetWithName.ComboBox(self, "Pivot To Align:")
        self.pivot_align_axis.addItem("Pivot X", "pivot_x")
        self.pivot_align_axis.addItem("Pivot Y", "pivot_y")
        self.pivot_align_axis.addItem("Pivot Z", "pivot_z")
        self.pivot_align_axis.setCurrentIndex(1)
        
        self.align_btn = GuiUtils.addButton(self, "Align To It")
        self.align_btn.clicked.connect(self.alignPrimaryAxis)
        
        self.bake_pivot_btn = GuiUtils.addButton(self, "Bake Pivot")
        self.bake_pivot_btn.clicked.connect(self.bakePivot)        
        self.auto_batch_btn = GuiUtils.addButton(self, "Batch All", "It will ignore the secondary alignment")                 
        self.auto_batch_btn.clicked.connect(self.batchAll)      
           
        self.secondary_axis = WidgetWithName.ComboBox(self, "Secondary Pivot Axis To Align:")
        self.secondary_axis.addItem("Pivot X", "pivot_x")
        self.secondary_axis.addItem("Pivot Y", "pivot_y")
        self.secondary_axis.addItem("Pivot Z", "pivot_z")
        
        self.secondary_dir_to_align = WidgetWithName.ComboBox(self, "Secondary Pivot Dir To Align:")
        self.secondary_dir_to_align.addItem("World X", "pivot_x")
        self.secondary_dir_to_align.addItem("World Y", "pivot_y")
        self.secondary_dir_to_align.addItem("World Z", "pivot_z")        
        self.secondary_dir_to_align.addItem("Custom Position", "custom_pos")
        self.secondary_dir_to_align.addItem("Ignore", "ignore")
        self.secondary_dir_to_align.setCurrentIndex(3)
        
        self.position_vector_vis = VectorVis.Vector3SpinBox(self)
        self.position_vector_vis.setMinMax(-0xfffffff, 0xfffffff)
        self.position_vector_vis.setVisMinimumWidth(10)
        self.position_vis = WidgetWithName.WidgetInstanceWithName(self.position_vector_vis, self, "Saved Position:")
    
        self.remember_btn = GuiUtils.addButton(self, "Remember Position")
        self.remember_btn.clicked.connect(self.rememberSelectPoint)
        self.align_secondary_pivot_btn = GuiUtils.addButton(self, "Align Secondary Pivot")
        self.align_secondary_pivot_btn.clicked.connect(self.alignSecondaryAxis)        
        
        self.to_zero_btn = GuiUtils.addButton(self, "Zero Rotation")
        self.to_zero_btn.clicked.connect(self.zeroRotation)
        
        self.vbox = QVBoxLayout(self)
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.setSpacing(5)
        self.vbox.addWidget(self.check_widget)
        self.vbox.addWidget(self.bake_if_mult)        
        self.vbox.addWidget(self.searching_method)
        self.vbox.addWidget(self.pivot_align_axis)
        self.vbox.addWidget(self.align_btn)
        self.vbox.addWidget(Separator.Separator(self))
        self.vbox.addWidget(self.invert_pivot)
        self.vbox.addWidget(self.bake_pivot_btn)
        self.vbox.addWidget(Separator.Separator(self))
        self.vbox.addWidget(self.secondary_axis)
        self.vbox.addWidget(self.secondary_dir_to_align)        
        self.vbox.addWidget(self.position_vis)        
        self.vbox.addWidget(self.remember_btn)        
        self.vbox.addWidget(self.align_secondary_pivot_btn)
        self.vbox.addWidget(Separator.Separator(self))
        self.vbox.addWidget(self.auto_batch_btn)  
        self.vbox.addWidget(self.to_zero_btn)
        
    def alignPrimaryAxis(self):
        PivotAlignmentFunction.pivotAlignmentMainAxis(self.pivot_align_axis.getCurrentActiveData(), 
                                                      self.searching_method.getCurrentActiveData(),
                                                      self.set_trans.isChecked(), self.set_ori.isChecked(),
                                                      self.bake_if_mult.isChecked())

    def invertPivot(self):
        PivotAlignmentFunction.invertPivotAxis(self.pivot_align_axis.getCurrentActiveData(),
                                               self.secondary_axis.getCurrentActiveData())
        
    def bakePivot(self):
        PivotAlignmentFunction.bakePivot()
        
    def rememberSelectPoint(self):
        vector = PivotAlignmentFunction.getCurrentSelectionPositon().get()
        print(vector)
        self.position_vector_vis.setValue(list(vector))
        
    def alignSecondaryAxis(self):
        PivotAlignmentFunction.pivotAlignmentSecondaryAxis(self.secondary_dir_to_align.getCurrentActiveData(), 
                                                           self.secondary_axis.getCurrentActiveData(),
                                                           self.pivot_align_axis.getCurrentActiveData(), 
                                                           self.position_vector_vis.getVector())
        
    def batchAll(self):
        self.alignPrimaryAxis()
        self.alignSecondaryAxis()
        self.bakePivot()    
        
    def zeroRotation(self):
        PivotAlignmentFunction.zeroRotation()


def createWidget(obj):
    return PivotAligment(obj)


def show():
    print("\n==== Start", WIDGET_TITLE_NAME, "=====\n")
    ui = PivotAligment()
    ui.show()
    return ui