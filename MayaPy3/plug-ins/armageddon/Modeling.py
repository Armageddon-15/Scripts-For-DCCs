# -*- coding: UTF-8 -*-

from .GUI import Separator, WidgetWithHeader, WidgetWithName
from .GUI import Utils as GuiUtils

from . import ModelingFunction
from . import BetterNormalFunction

from .GUI.MayaMainWindow import setWidgetAsMayaMainWindow

from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *

PRIORITY = 1
WIDGET_TITLE_NAME = "Modeling"
WIDGET_OBJECT_NAME = "modeling"


class AlignmentWidget(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(AlignmentWidget,self).__init__(parent, *args, **kwargs)
        
        if parent is None:
            setWidgetAsMayaMainWindow(self, WIDGET_TITLE_NAME, WIDGET_OBJECT_NAME)
        
        self.align_header = WidgetWithHeader.WidgetWithHeader(self, "Alignment")
        
        self.max_length = WidgetWithName.SpinBox(self, "Max Trace Length:")
        self.max_length.setMaxValue(9999999)
        self.max_length.setValue(100000)
        
        self.point_align_line_btn = GuiUtils.addButton(self, "Point Align Line",
                                                       "将一些点对齐到一条线上，只能使用最近距离\n"
                                                       "操作如下：\n"
                                                       "1.选定一些点，其中前两个点为确定线段的点\n"
                                                       "  其余点为需要移动的点\n"
                                                       "2.或者使用多组件选择，无关顺序，所选的第一条\n"
                                                       "  边为对齐边，其余点为需要用到的点")
        self.point_align_line_btn.clicked.connect(self.pointAlignLine)        
        
        self.face_align_combo_box = WidgetWithName.ComboBox(self, "Face Align Director:")
        self.face_align_combo_box.setComboBoxToolTip("Hi")
        self.face_align_combo_box.addItem("Closest", "closest")
        self.face_align_combo_box.addItem("Normal", "normal")  
        self.face_align_combo_box.addItem("Pivot X", "pivot_x")
        self.face_align_combo_box.addItem("Pivot Y", "pivot_y")
        self.face_align_combo_box.addItem("Pivot Z", "pivot_z")
        
        self.point_align_face_btn = GuiUtils.addButton(self, "Point Align Face",
                                                   "将一些点对齐到一个平面上，根据上面的选单调整位置\n"
                                                   "操作如下：\n"
                                                   "1.选定一些点，其中前三个点为确定线段的点\n"
                                                   "  其余点为需要移动的点\n"
                                                   "2.或者使用多组件选择，无关顺序，所选的第一个\n"
                                                   "  面为对齐平面，其余点为需要用到的点")
        
        self.point_align_face_btn.clicked.connect(self.pointAlingFace)
        
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
        
    def pointAlingFace(self):
        ModelingFunction.verticesAlignFace(self.face_align_combo_box.getCurrentActiveData(), 
                                           self.max_length.getValue())
     
     
        
class BetterNormal(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(BetterNormal,self).__init__(parent, *args, **kwargs)
        
        if parent is None:
            setWidgetAsMayaMainWindow(self, WIDGET_TITLE_NAME, WIDGET_OBJECT_NAME)
            
        
        self.header = WidgetWithHeader.WidgetWithHeader(self, "Better Normal")
        
        self.area_weight = WidgetWithName.ViewerSlider(self, "Area Weight")
        self.area_weight.setValue(1)
        self.area_weight.setMaximumValue(20)
        self.area_weight.valueChanged.connect(self.liveUpdateBetterNormal)
        self.distance_weight = WidgetWithName.ViewerSlider(self, "Distance Weight")
        self.distance_weight.setValue(1)
        self.distance_weight.setMaximumValue(20)
        self.distance_weight.valueChanged.connect(self.liveUpdateBetterNormal)
        self.size_scale = WidgetWithName.ViewerSlider(self, "Size Scale")
        self.size_scale.setValue(1)
        self.size_scale.setPrecise(0.1)        
        self.size_scale.setMaximumValue(100)
        self.size_scale.valueChanged.connect(self.liveUpdateBetterNormal)
        self.threshold = WidgetWithName.ViewerSlider(self, "Threshold")
        self.threshold.setPrecise(0.01)
        self.threshold.setMaximumValue(1)
        self.threshold.setMinimumValue(0)
        self.threshold.valueChanged.connect(self.liveUpdateBetterNormal)
        self.live_update_checkbox = GuiUtils.addWidget(self, QCheckBox, "Live Update", "")
        self.live_update_checkbox.toggled.connect(self.liveUpdateToggle)
        
        self.apply_btn = GuiUtils.addButton(self, "Apply")
        self.apply_btn.clicked.connect(self.betterNormalExcute)
        
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
        
    def betterNormalExcute(self):
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

        
        
class Modeling(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(Modeling, self).__init__(parent, *args, **kwargs)
                
        if parent is None:
            setWidgetAsMayaMainWindow(self, WIDGET_TITLE_NAME, WIDGET_OBJECT_NAME)
            
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
    print("\n==== Start", WIDGET_TITLE_NAME, "=====\n")
    ui = Modeling()
    ui.show()
    return ui