from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *


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