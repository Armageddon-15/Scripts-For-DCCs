# -*- coding: UTF-8 -*-

from GUI import Separator, WidgetWithHeader, WidgetWithName
import GUI.Utils as GuiUtils

import ModelingFunction

from GUI.MayaMainWindow import setWidgetAsMayaMainWindow

from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *

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
        
        



def show():
    print("\n==== Start", WIDGET_TITLE_NAME, "=====\n")
    ui = AlignmentWidget()
    ui.show()
    return ui