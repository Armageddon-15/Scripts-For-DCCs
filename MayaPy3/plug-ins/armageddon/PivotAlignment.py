# -*- coding: UTF-8 -*-

from .GUI import Separator, WidgetWithHeader, WidgetWithName, VectorVis
from .GUI import Utils as GuiUtils
from .Translate import TranslatorManager

from . import PivotAlignmentFunction

from .GUI import PanelWidget

from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *

PRIORITY = 2
WIDGET_TITLE_NAME = "Pivot Align Tube"
WIDGET_OBJECT_NAME = "pivot_align_tube"

class PivotAlignment(PanelWidget.PanelWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(PivotAlignment, self).__init__(parent, *args, **kwargs)
            
        self.check_widget = QFrame(self)
        self.check_hbox = QHBoxLayout(self.check_widget)
        self.check_hbox.setContentsMargins(0,0,0,0)
        self.set_trans = GuiUtils.addWidget(self, QCheckBox)
        TranslatorManager.getTranslator().addTranslate(self.set_trans.setText, "Translation")
        self.set_trans.setChecked(True)
        self.set_ori = GuiUtils.addWidget(self, QCheckBox)
        TranslatorManager.getTranslator().addTranslate(self.set_ori.setText, "Orientation")
        self.set_ori.setChecked(True)
        self.check_hbox.addWidget(self.set_trans)
        self.check_hbox.addWidget(self.set_ori)
        
        self.bake_if_mult = GuiUtils.addWidget(self, QCheckBox)
        TranslatorManager.getTranslator().addTranslate(self.bake_if_mult.setText, "Automatic bake pivot if more than one")
        TranslatorManager.getTranslator().addTranslate(self.bake_if_mult.setToolTip, "PA_BIM_Tip")
        self.bake_if_mult.setChecked(True) 

        self.searching_method = WidgetWithName.ComboBox(self)
        TranslatorManager.getTranslator().addTranslate(self.searching_method.getNameWidget().setText, "Searching Method:")
        self.searching_method.addItem("Max", "max")
        self.searching_method.addItem("Min", "min")
        self.searching_method.addItem("Select Loop", "selected_loop")
        self.searching_method.addItem("Not For Transform", "ignore")
        TranslatorManager.getTranslator().addTranslate(self.searching_method.getNameWidget().setToolTip, "PA_SM_Tip")
        TranslatorManager.getTranslator().addItemTranslate(self.searching_method.getRightWidget())
        
        self.pivot_align_axis = WidgetWithName.ComboBox(self, "Pivot Axis To Align:")
        TranslatorManager.getTranslator().addTranslate(self.pivot_align_axis.getNameWidget().setText, "Pivot Axis To Align:")
        self.pivot_align_axis.addItem("Pivot X", "pivot_x")
        self.pivot_align_axis.addItem("Pivot Y", "pivot_y")
        self.pivot_align_axis.addItem("Pivot Z", "pivot_z")
        TranslatorManager.getTranslator().addItemTranslate(self.pivot_align_axis.getRightWidget())
        self.pivot_align_axis.setCurrentIndex(1)
        
        self.align_btn = GuiUtils.addButton(self)
        TranslatorManager.getTranslator().addTranslate(self.align_btn.setText, "Align")
        self.align_btn.clicked.connect(self.alignPrimaryAxis)

        self.auto_batch_btn = GuiUtils.addButton(self, "Batch All", "It will ignore the secondary alignment")
        TranslatorManager.getTranslator().addTranslate(self.auto_batch_btn.setText, "Batch All")
        TranslatorManager.getTranslator().addTranslate(self.auto_batch_btn.setToolTip, "PA_AB_Btn_Tip")

        self.invert_pivot = GuiUtils.addButton(self)
        TranslatorManager.getTranslator().addTranslate(self.invert_pivot.setText, "Invert Pivot")
        TranslatorManager.getTranslator().addTranslate(self.invert_pivot.setToolTip, "PA_IP_Btn_Tip")
        self.invert_pivot.clicked.connect(self.invertPivot)
        
        self.bake_pivot_btn = GuiUtils.addButton(self)
        TranslatorManager.getTranslator().addTranslate(self.bake_pivot_btn.setText, "Bake Pivot")
        self.bake_pivot_btn.clicked.connect(self.bakePivot)
           
        self.secondary_axis = WidgetWithName.ComboBox(self)
        TranslatorManager.getTranslator().addTranslate(self.secondary_axis.getNameWidget().setText, "Secondary Pivot Axis To Align:")
        self.secondary_axis.addItem("Pivot X", "pivot_x")
        self.secondary_axis.addItem("Pivot Y", "pivot_y")
        self.secondary_axis.addItem("Pivot Z", "pivot_z")
        TranslatorManager.getTranslator().addItemTranslate(self.secondary_axis.getRightWidget())
        
        self.secondary_dir_to_align = WidgetWithName.ComboBox(self)
        TranslatorManager.getTranslator().addTranslate(self.secondary_dir_to_align.getNameWidget().setText, "Secondary Pivot Dir To Align:")
        self.secondary_dir_to_align.addItem("World X", "world_x")
        self.secondary_dir_to_align.addItem("World Y", "world_y")
        self.secondary_dir_to_align.addItem("World Z", "world_z")
        self.secondary_dir_to_align.addItem("Custom Position", "custom_pos")
        self.secondary_dir_to_align.addItem("Ignore", "ignore")
        TranslatorManager.getTranslator().addItemTranslate(self.secondary_dir_to_align.getRightWidget())
        self.secondary_dir_to_align.setCurrentIndex(3)
        
        self.position_vector_vis = VectorVis.Vector3SpinBox(self)
        self.position_vector_vis.setMinMax(-0xfffffff, 0xfffffff)
        self.position_vector_vis.setVisMinimumWidth(10)
        self.position_vis = WidgetWithName.WidgetInstanceWithName(self.position_vector_vis, self)
        TranslatorManager.getTranslator().addTranslate(self.position_vis.getNameWidget().setText, "Custom Saved Position:")
    
        self.remember_btn = GuiUtils.addButton(self)
        TranslatorManager.getTranslator().addTranslate(self.remember_btn.setText, "Remember Position")
        self.remember_btn.clicked.connect(self.rememberSelectPoint)
        self.align_secondary_pivot_btn = GuiUtils.addButton(self)
        TranslatorManager.getTranslator().addTranslate(self.align_secondary_pivot_btn.setText, "Align Secondary Pivot Axis")
        self.align_secondary_pivot_btn.clicked.connect(self.alignSecondaryAxis)        

        self.auto_batch_btn.clicked.connect(self.batchAll)
        self.to_zero_btn = GuiUtils.addButton(self, "Zero Rotation")
        TranslatorManager.getTranslator().addTranslate(self.to_zero_btn.setText, "Zero Rotation")
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
    return PivotAlignment(obj)


def show():
    ui = PivotAlignment()
    ui.showWindow()
    return ui