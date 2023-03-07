import maya.cmds as cmd
from maya import OpenMayaUI as omui 

from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance 


mayaMainWindowPtr = omui.MQtUtil.mainWindow() 
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget) 

class RadioGroup(QWidget):
    def __init__(self, text="", *args, **kwargs):
        super(RadioGroup, self).__init__(**kwargs)
        self.text_label = QLabel(self)
        self.radio_group = []
        self.hbox = QHBoxLayout(self)
        
        self.setTitleText(text)
        
    def setTitleText(self, text):
        self.text_label.setText(text)
        
    def addRadioBtn(self, text):
        radio = QRadioButton(self)
        radio.setText(text)
        self.radio_group.append(radio)
        
    def deleteRadioBtn(self, ind):
        self.radio_group.pop(ind)
        
    def getActiveRadio(self):
        for btn in self.radio_group:
            if btn.isChecked():
                return btn
        return None
        
    def layoutWidget(self):
        for i in reversed(range(0, self.hbox.count())):
            self.hbox.itemAt(i).widget().hide()
            self.hbox.removeWidget(self.hbox.itemAt(i).widget())
            
        self.hbox.addWidget(self.text_label)
        for btn in self.radio_group:
            self.hbox.addWidget(btn)
        
        self.radio_group[0].setChecked(True)


class CreatePolygonUI(QWidget):
    def __init__(self, *args, **kwargs):
        super(CreatePolygonUI, self).__init__(*args, **kwargs)
        self.setParent(mayaMainWindow)
        self.setWindowFlags(Qt.Window)
        self.setObjectName('CreatePolygonUI_2')
        self.setWindowTitle('Create polygon')
        self.setGeometry(50, 50, 250, 150)
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)
        self.vbox.setAlignment(Qt.AlignTop)
        
        self.axis_radio_group = []
        self.addRadioBtn()
        
        self.pivot_btn = QPushButton(self)
        self.pivot_btn.setText("Set Pivot")
        self.pivot_btn.clicked.connect(self.setPivotPosition)
        
        self.bbox_btn = QPushButton(self)
        self.bbox_btn.setText("To World Center")
        self.bbox_btn.clicked.connect(self.setPosition)
        
        self.vbox.addWidget(self.pivot_btn)
        self.vbox.addWidget(self.bbox_btn)
        
    def addRadioBtn(self):
        x_radio_group = RadioGroup("X-aixs:", self)
        y_radio_group = RadioGroup("Y-aixs:", self)
        z_radio_group = RadioGroup("Z-aixs:", self)
        x_radio_group.addRadioBtn("Min")
        x_radio_group.addRadioBtn("Mid")
        x_radio_group.addRadioBtn("Max")
        x_radio_group.layoutWidget()
        self.vbox.addWidget(x_radio_group)
        y_radio_group.addRadioBtn("Min")
        y_radio_group.addRadioBtn("Mid")
        y_radio_group.addRadioBtn("Max")
        y_radio_group.layoutWidget()
        self.vbox.addWidget(y_radio_group)
        z_radio_group.addRadioBtn("Min")
        z_radio_group.addRadioBtn("Mid")
        z_radio_group.addRadioBtn("Max")
        z_radio_group.layoutWidget()
        self.vbox.addWidget(z_radio_group)
        self.axis_radio_group = [x_radio_group, y_radio_group, z_radio_group]
        
    def getAxisState(self):
        text = []
        for rad_group in self.axis_radio_group:
            rad = rad_group.getActiveRadio()
            if rad is not None:
                text.append(rad.text()) 
            else:
                text.append(u"Min")
        
        return text
    
    def setPivotPosition(self):
        axises = self.getAxisState()
        ss = checkSelect(l=True)
        for sel in ss:
            pos = getBBoxPosByState(sel, axises)
            setPivotPosition(sel, pos)
            
    def setPosition(self):
        axises = self.getAxisState()
        ss = checkSelect(l=True)
        for sel in ss:
            cmd.move(0, 0, 0, sel, rpr=True)


def getBBoxPosByState(obj, state):
        pos = []
        bbox = cmd.exactWorldBoundingBox(obj)
        for i in range(len(state)):
            if state[i]== u"Min":
                pos.append(bbox[i])
            elif state[i] == u"Max":
                pos.append(bbox[i+3])
            elif state[i] == u"Mid":
                pos.append(average2(bbox[i], bbox[i+3]))
        
        return pos
        
def checkSelect(*args, **kwargs):
    list_select = []
    if cmd.ls(sl = True) != []:
        list_select = cmd.ls(sl=True, *args, **kwargs)
        return list_select
    else:
        return []


def average2(a, b):
    return (a+b)/2

        
def setPivotPosition(obj, pos):
    cmd.xform(obj, pivots=pos, worldSpace=True)


        
            
def main():
    ui = CreatePolygonUI()
    ui.show()
    return ui
    
if __name__ == '__main__':
    main()
