from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QComboBox, QSpinBox, QAbstractSpinBox
from PySide2.QtCore import Qt

class WidgetWithName(QWidget):
    def __init__(self, widget_type, parent=None, name="", layout_type=QHBoxLayout, *args, **kwargs):
        super(WidgetWithName, self).__init__(parent, *args, **kwargs)
        self.name = QLabel(self)
        self.name.setText(name)
        
        self.right_widget = None
        self.setRightWidget(widget_type)
        
        self.layout_box = layout_type(self)
        self.layout_box.setContentsMargins(0,0,0,0)
        self.layout_box.addWidget(self.name)
        self.layout_box.addWidget(self.right_widget)
        
    def setRightWidget(self, widget_type):
        self.right_widget = widget_type(self)
        

class ComboBox(WidgetWithName):
    def __init__(self, *args, **kwargs):
        super(ComboBox, self).__init__(QComboBox, *args, **kwargs)

    def addItem(self, name, data=None):
        self.right_widget.addItem(name, data)
        
    def addItems(self, items):
        self.right_widget.addItems(items)
        
    def getCurrentActiveItem(self):
        return self.right_widget.currentText()
    
    def getCurrentActiveData(self):
        return self.right_widget.currentData()
    
    def setComboBoxToolTip(self, tip):
        self.right_widget.setToolTip(tip)
        
        
class SpinBox(WidgetWithName):
    def __init__(self, *args, **kwargs):
        super(SpinBox, self).__init__(QSpinBox, *args, **kwargs)
        self.right_widget.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.right_widget.setAlignment(Qt.AlignRight)

    
    def setValue(self, v):
        self.right_widget.setValue(v)
        
    def getValue(self):
        return self.right_widget.value()
    
    def setMaxValue(self, v):
        self.right_widget.setMaximum(v)

    def setMinValue(self, v):
        self.right_widget.setMinimum(v)