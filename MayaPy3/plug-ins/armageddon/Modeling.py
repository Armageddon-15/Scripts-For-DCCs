# -*- coding: UTF-8 -*-

from .GUI import WidgetWithHeader, WidgetWithName
from .GUI import Utils as GuiUtils

from .Translate import TranslatorManager

from . import ModelingFunction
from . import BetterNormalFunction

from .GUI import PanelWidget

from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *

PRIORITY = 1
WIDGET_TITLE_NAME = "Modeling"
WIDGET_OBJECT_NAME = "modeling"


class AlignmentWidget(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(AlignmentWidget,self).__init__(parent, *args, **kwargs)

        self.align_header = WidgetWithHeader.WidgetWithHeader(self)
        TranslatorManager.getTranslator().addTranslate(self.align_header.header.setText, "Alignment")
        
        self.max_length = WidgetWithName.SpinBox(self)
        TranslatorManager.getTranslator().addTranslate(self.max_length.getNameWidget().setText, "Max Trace Length:")
        self.max_length.setMaxValue(9999999)
        self.max_length.setValue(100000)
        
        self.point_align_line_btn = GuiUtils.addButton(self)
        TranslatorManager.getTranslator().addTranslate(self.point_align_line_btn.setText, "Point Align Line")
        TranslatorManager.getTranslator().addTranslate(self.point_align_line_btn.setToolTip, "M_AW_PAL_Btn_Tip")
        self.point_align_line_btn.clicked.connect(self.pointAlignLine)        
        
        self.face_align_combo_box = WidgetWithName.ComboBox(self)
        TranslatorManager.getTranslator().addTranslate(self.face_align_combo_box.getNameWidget().setText, "Face Align Direction:")
        TranslatorManager.getTranslator().addTranslate(self.face_align_combo_box.getNameWidget().setToolTip, "M_AW_FACB_Tip")
        self.face_align_combo_box.addItem("Closest", "closest")
        self.face_align_combo_box.addItem("Normal", "normal")  
        self.face_align_combo_box.addItem("Pivot X", "pivot_x")
        self.face_align_combo_box.addItem("Pivot Y", "pivot_y")
        self.face_align_combo_box.addItem("Pivot Z", "pivot_z")

        TranslatorManager.getTranslator().addItemTranslate(self.face_align_combo_box.getRightWidget())
        
        self.point_align_face_btn = GuiUtils.addButton(self)
        TranslatorManager.getTranslator().addTranslate(self.point_align_face_btn.setText, "Point Align Face")
        TranslatorManager.getTranslator().addTranslate(self.point_align_face_btn.setToolTip, "M_AW_PAF_Btn_Tip")
        
        self.point_align_face_btn.clicked.connect(self.pointAlignFace)
        
        self.align_header.addWidget(self.max_length)
        self.align_header.addWidget(self.point_align_line_btn)
        self.align_header.addWidget(self.face_align_combo_box)
        self.align_header.addWidget(self.point_align_face_btn)
        
        self.vbox = QVBoxLayout(self)
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.setSpacing(2)
        self.vbox.addWidget(self.align_header)
        
    def pointAlignLine(self):
        ModelingFunction.verticesAlignLine()
        
    def pointAlignFace(self):
        ModelingFunction.verticesAlignFace(self.face_align_combo_box.getCurrentActiveData(), 
                                           self.max_length.getValue())
     
     
        
class BetterNormal(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(BetterNormal,self).__init__(parent, *args, **kwargs)
        
        self.header = WidgetWithHeader.WidgetWithHeader(self)
        TranslatorManager.getTranslator().addTranslate(self.header.header.setText, "Better Normal")
        
        self.area_weight = WidgetWithName.ViewerSlider(self)
        TranslatorManager.getTranslator().addTranslate(self.area_weight.getNameWidget().setText, "Area Weight")
        self.area_weight.setValue(1)
        self.area_weight.setMaximumValue(20)
        self.area_weight.valueChanged.connect(self.liveUpdateBetterNormal)
        self.distance_weight = WidgetWithName.ViewerSlider(self)
        TranslatorManager.getTranslator().addTranslate(self.distance_weight.getNameWidget().setText, "Distance Weight")
        self.distance_weight.setValue(1)
        self.distance_weight.setMaximumValue(20)
        self.distance_weight.valueChanged.connect(self.liveUpdateBetterNormal)
        self.size_scale = WidgetWithName.ViewerSlider(self)
        TranslatorManager.getTranslator().addTranslate(self.size_scale.getNameWidget().setText, "Size Scale")
        self.size_scale.setValue(1)
        self.size_scale.setPrecise(0.1)        
        self.size_scale.setMaximumValue(100)
        self.size_scale.valueChanged.connect(self.liveUpdateBetterNormal)
        self.threshold = WidgetWithName.ViewerSlider(self)
        TranslatorManager.getTranslator().addTranslate(self.threshold.getNameWidget().setText, "Threshold")
        self.threshold.setPrecise(0.01)
        self.threshold.setMaximumValue(1)
        self.threshold.setMinimumValue(0)
        self.threshold.valueChanged.connect(self.liveUpdateBetterNormal)
        self.live_update_checkbox = GuiUtils.addWidget(self, QCheckBox)
        TranslatorManager.getTranslator().addTranslate(self.live_update_checkbox.setText, "Live Update")
        self.live_update_checkbox.toggled.connect(self.liveUpdateToggle)
        
        self.apply_btn = GuiUtils.addButton(self)
        TranslatorManager.getTranslator().addTranslate(self.apply_btn.setText, "Apply")
        self.apply_btn.clicked.connect(self.betterNormalExecute)
        
        self.header.addWidget(self.area_weight)
        self.header.addWidget(self.distance_weight)
        self.header.addWidget(self.size_scale)
        self.header.addWidget(self.threshold)
        
        self.header.addWidget(self.live_update_checkbox)
        self.header.addWidget(self.apply_btn)
        
        self.vbox = QVBoxLayout(self)
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.setSpacing(2)

        self.vbox.addWidget(self.header)
        
    def liveUpdateToggle(self, b):
        if b:
            BetterNormalFunction.updateBackendSelection()
    
    def liveUpdateBetterNormal(self):
        if self.live_update_checkbox.isChecked():
            area, dist = self.area_weight.getSliderValue(), self.distance_weight.getSliderValue()
            size, thres = self.size_scale.getSliderValue(), self.threshold.getSliderValue()            
            
            BetterNormalFunction.betterNormalLiveUpdate(thres, area, dist, size)
        
    def betterNormalExecute(self):
        area, dist = self.area_weight.getSliderValue(), self.distance_weight.getSliderValue()
        size, thres = self.size_scale.getSliderValue(), self.threshold.getSliderValue()
        BetterNormalFunction.betterNormalExecuteOnce(thres, area, dist, size)  
        
        self.live_update_checkbox.setChecked(False)
              
        # print(area, dist)
        # print(size, thres)
        # print(self.live_update_checkbox.isChecked())
        
    def destroy(self, *args, **kwargs):
        super(BetterNormal, self).destroy(*args, **kwargs)
        BetterNormalFunction.releaseBackendSelection()

        
        
class Modeling(PanelWidget.PanelWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(Modeling, self).__init__(parent, *args, **kwargs)
            
        self.alignment_widget = AlignmentWidget(self)
        self.better_normal_widget = BetterNormal(self)
        
        self.vbox = QVBoxLayout(self)
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.setSpacing(2)
        self.vbox.setContentsMargins(0,0,0,0)
        
        self.vbox.addWidget(self.alignment_widget)
        self.vbox.addWidget(self.better_normal_widget)




def createWidget(obj):
    return Modeling(obj)


def show():
    ui = Modeling()
    ui.showWindow()
    return ui