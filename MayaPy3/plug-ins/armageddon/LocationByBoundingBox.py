# -*- coding: UTF-8 -*-
from . import Parameters
from . import LocationByBoundingBoxFunction as Func

from .GUI import Separator, RadioGroup, WidgetWithHeader
from .GUI import Utils as GuiUtils

from .GUI.MayaMainWindow import setWidgetAsMayaMainWindow

from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *

PRIORITY = 0
WIDGET_TITLE_NAME = "Transformation And Bounding Box"
WIDGET_OBJECT_NAME = "transformation_and_bounding_box"


class BoundingBoxStateWidget(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(BoundingBoxStateWidget, self).__init__(*args, **kwargs)
        self.main = parent
        
        self.axis_radio_group = []
        
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(5)
        
        self.__addRadioBtn()
        
        self.actual_size_check = QCheckBox(self)
        self.actual_size_check.setCheckState(Qt.Checked)
        self.actual_size_check.setText("Actual Size")
        self.actual_size_check.setToolTip("transform的bbox是变换后的shape的bbox的bbox，"
                                          "基本没有实际意义，所以默认勾选")
        self.exclude_children = QCheckBox(self)
        self.exclude_children.setText("Only Selected")
        self.exclude_children.setToolTip("勾选时bbox不包括子集")
        self.one_large_bbox = QCheckBox(self)
        self.one_large_bbox.setText("One Large BBox")
        self.one_large_bbox.setToolTip("勾选时将所选所有物体看成一个整体")     
           
        self.check_box_frame = QFrame(self)
        self.frame_hbox = QHBoxLayout(self.check_box_frame)
        self.frame_hbox.setContentsMargins(0, 1, 0, 1)        
        self.frame_hbox.setAlignment(Qt.AlignHCenter)
        self.frame_hbox.addWidget(self.actual_size_check)
        self.frame_hbox.addWidget(self.exclude_children)
        self.frame_hbox.addWidget(self.one_large_bbox)        
     
        self.inspect_bbox_setting = GuiUtils.addButton(self, "Inspect Settings",
                                                       "检查数据，debug用")
        self.inspect_bbox_setting.clicked.connect(self.inspectBBoxSetting)
        
        self.vis_bbox = GuiUtils.addButton(self, "看看你的",
                                           "生成所选取物体的bbox，一个立方体")
        self.vis_bbox.clicked.connect(self.visualizeBBox)
        
        self.vbox.addWidget(self.check_box_frame)        
        self.vbox.addWidget(self.inspect_bbox_setting)
        self.vbox.addWidget(self.vis_bbox)

    def __addRadioBtn(self):
        x_radio_group = RadioGroup.RadioGroup(self, "X-aixs:")
        y_radio_group = RadioGroup.RadioGroup(self, "Y-aixs:")
        z_radio_group = RadioGroup.RadioGroup(self, "Z-aixs:")
        
        x_radio_group.addRadioBtn("Min")
        x_radio_group.addRadioBtn("Mid")
        x_radio_group.addRadioBtn("Max")
        x_radio_group.addRadioBtn("Ignore")
        x_radio_group.layoutWidget()
        self.vbox.addWidget(x_radio_group)
        
        y_radio_group.addRadioBtn("Min")
        y_radio_group.addRadioBtn("Mid")
        y_radio_group.addRadioBtn("Max")
        y_radio_group.addRadioBtn("Ignore")        
        y_radio_group.layoutWidget()
        self.vbox.addWidget(y_radio_group)
        
        z_radio_group.addRadioBtn("Min")
        z_radio_group.addRadioBtn("Mid")
        z_radio_group.addRadioBtn("Max")
        z_radio_group.addRadioBtn("Ignore")         
        z_radio_group.layoutWidget()
        self.vbox.addWidget(z_radio_group)
        
        self.axis_radio_group = [x_radio_group, y_radio_group, z_radio_group]
        
    def inspectBBoxSetting(self):
        print (self.getAllSettings())
    
    def visualizeBBox(self):
        Func.visualizeSelectedBoundingBox(self.getIfOneLargeBBox(), 
                                          self.getIfActualSize(), 
                                          self.getIfExcludeChildren())
       
    def getState(self):
        result = []
        for radio_group in self.axis_radio_group:
            rad = radio_group.getActiveRadio()
            if rad is not None:
                result.append(rad.text()) 
            else:
                result.append(u"Min")
        
        return result
    
    def getIfActualSize(self):
        return self.actual_size_check.isChecked()
    
    def getIfExcludeChildren(self):
        return self.exclude_children.isChecked()
    
    def getIfOneLargeBBox(self):
        return self.one_large_bbox.isChecked()
    
    def getAllSettings(self):
        return (self.getState(), self.getIfActualSize(), 
                self.getIfExcludeChildren(), self.getIfOneLargeBBox())
            
        


class LocationByBoundingBox(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(LocationByBoundingBox, self).__init__(*args, **kwargs)
        if parent is None:
            setWidgetAsMayaMainWindow(self, WIDGET_TITLE_NAME, WIDGET_OBJECT_NAME)

        # self.setGeometry(50, 50, 250, 150)
        
        self.vbox = QVBoxLayout(self)
        # self.vbox.setContentsMargins(5, 0, 5, 0)
        self.vbox.setSpacing(1)
        self.vbox.setAlignment(Qt.AlignTop)
        
        self.bbox_settings_widget = WidgetWithHeader.WidgetWithHeader(self, "Bounding Box Settings:")
        self.bbox_settings = BoundingBoxStateWidget(self)
        self.bbox_settings_widget.addWidget(self.bbox_settings)

        self.separator = Separator.Separator(self, 20)
        
        self.move_settings_widget = WidgetWithHeader.WidgetWithHeader(self, "Moving:")
        
        self.move_exclude_children = GuiUtils.addWidget(self, QCheckBox,
                                                        "Exclude Children", 
                                                        "勾选时移动将不包括子集")
                       
        self.move_to_world_center_by_group_bbox = GuiUtils.addButton(self, "Move To World Center By BBox",
                                                                 "根据bbox选项移动到对应位置\n"
                                                                    "要注意only selected 和 exclude children 勾选情况，\n"
                                                                    "不一致时移动可能并非预想情况\n"
                                                                    "勾选one large bbox时所选物体将会根据整体的bbox移动相同的距离\n"
                                                                    "不勾选时则每个选择的物体都会根据自己的bbox移动")
        self.move_to_world_center_by_group_bbox.clicked.connect(self.moveToWorldCenterByGroupBBox)

        self.set_pivot_by_bbox = GuiUtils.addButton(self, "Move Pivot By BBox",
                                                    "根据bbox选项移动枢轴")
        self.set_pivot_by_bbox.clicked.connect(self.setPivotByBBox)
        
        self.keep_pivot_offset = GuiUtils.addWidget(self, QCheckBox,
                                                    "Keep Pivot Offset",
                                                    "移动后保持枢轴对物体的相对位置，\n"
                                                    "仅对此选项之后的操作有用,\n"
                                                    "一般第一个不勾选，第二个勾选")
        
        self.move_to_pivot_by_bbox = GuiUtils.addButton(self, "Move To Pivot By BBox",
                                                        "根据bbox选项移动物体到枢轴所在位置，\n"
                                                        "只能根据每个物体的bbox操作，\n"
                                                        "所以one larget bbox对这个选项没用")
        self.move_to_pivot_by_bbox.clicked.connect(self.moveToPivotByBBox) 
        
        self.move_to_world_center_by_pivot = GuiUtils.addButton(self, "Move To World Center By Pivot",
                                                                "和bbox无关，根据枢轴位置移动到世界坐标中心") 
        self.move_to_world_center_by_pivot.clicked.connect(self.moveToWorldCenterByPivot)
              
        self.move_settings_widget.addWidget(self.move_exclude_children)
        self.move_settings_widget.addWidget(self.move_to_world_center_by_group_bbox)
        self.move_settings_widget.addWidget(self.set_pivot_by_bbox)
        self.move_settings_widget.addWidget(self.keep_pivot_offset)        
        self.move_settings_widget.addWidget(self.move_to_pivot_by_bbox)
        self.move_settings_widget.addWidget(self.move_to_world_center_by_pivot)    
        
        self.vbox.addWidget(self.bbox_settings_widget)
        self.vbox.addWidget(self.separator)
        self.vbox.addWidget(self.move_settings_widget)
        
    def getIfMoveExcludeChildren(self):
        return self.move_exclude_children.isChecked()
        
    def getIfKeepPivotOffset(self):
        return self.keep_pivot_offset.isChecked()      
      
    def moveToWorldCenterByGroupBBox(self):
        state, actual_size, ex_c, one_large_bbox = self.bbox_settings.getAllSettings()
        if one_large_bbox:
            Func.moveToWorldCenterByGroupBBox(state, self.getIfMoveExcludeChildren(), actual_size, ex_c)
        else:
            Func.eachMoveToWorldCenterByEachBBox(state, self.getIfMoveExcludeChildren(), actual_size, ex_c)
        
    def setPivotByBBox(self):
        state, actual_size, ex_c, one_large_bbox = self.bbox_settings.getAllSettings()   
        Func.setPivotByBoundingBox(state, one_large_bbox, actual_size, ex_c)   
        
    def moveToPivotByBBox(self):
        state, actual_size, ex_c, one_large_bbox = self.bbox_settings.getAllSettings()
        Func.moveToPivotByBBox(state, self.getIfMoveExcludeChildren(),
                               self.getIfKeepPivotOffset(), actual_size, ex_c)         

    def moveToWorldCenterByPivot(self):
        Func.moveToWorldCenterByPivot(self.getIfMoveExcludeChildren(), self.getIfKeepPivotOffset())           
        

def createWidget(obj):
    return LocationByBoundingBox(obj)


def show():
    print("\n==== Start", WIDGET_TITLE_NAME, "=====\n")
    ui = LocationByBoundingBox()
    ui.show()
    return ui
    
if __name__ == '__main__':
    show()
