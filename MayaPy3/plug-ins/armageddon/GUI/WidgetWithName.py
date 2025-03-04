from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QComboBox, QSpinBox, QAbstractSpinBox, QDoubleSpinBox, QLineEdit
from PySide2.QtCore import Qt, Signal
from .SliderWithValueViewer import SliderWithViewer

from typing import Type, TypeVar, Generic

T = TypeVar("T")

class WidgetWithName(Generic[T], QWidget):
    def __init__(self, widget_type: Type[T], parent=None, name="", layout_type=QHBoxLayout, *args, **kwargs):
        super(WidgetWithName, self).__init__(parent, *args, **kwargs)
        self.name = QLabel(self)
        self.name.setText(name)
        
        self.right_widget = widget_type(self)
        
        self.layout_box = layout_type(self)
        self.layout_box.setContentsMargins(0,0,0,0)
        self.layout_box.addWidget(self.name)
        self.layout_box.addWidget(self.right_widget)
        
    def setRightWidget(self, widget_type):
        self.right_widget = widget_type(self)

    def getRightWidget(self) -> T:
        return self.right_widget

    def getNameWidget(self):
        return self.name
        
        
class WidgetInstanceWithName(QWidget):
    def __init__(self, widget, parent=None, name="", layout_type=QHBoxLayout, *args, **kwargs):
        super(WidgetInstanceWithName, self).__init__(parent, *args, **kwargs)
        self.name = QLabel(self)
        self.name.setText(name)
        
        self.right_widget = widget
        
        self.layout_box = layout_type(self)
        self.layout_box.setContentsMargins(0,0,0,0)
        self.layout_box.addWidget(self.name)
        self.layout_box.addWidget(self.right_widget)

    def getNameWidget(self):
        return self.name
        

class ComboBox(WidgetWithName[QComboBox]):
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
        
    def setCurrentIndex(self, i):
        self.right_widget.setCurrentIndex(i)
        
        
class SpinBox(WidgetWithName[QSpinBox]):
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


class LineEdit(WidgetWithName[QLineEdit]):
    def __init__(self, *args, **kwargs):
        super(LineEdit, self).__init__(QLineEdit, *args, **kwargs)
        self.right_widget.setAlignment(Qt.AlignRight)

    def setValue(self, v):
        self.right_widget.setText(v)

    def getValue(self):
        return self.right_widget.text()


class DoubleSpinBox(WidgetWithName[QDoubleSpinBox]):
    def __init__(self, *args, **kwargs):
        super(DoubleSpinBox, self).__init__(QDoubleSpinBox, *args, **kwargs)
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
        
            
class ViewerSlider(WidgetWithName[SliderWithViewer]):
    valueChanged = Signal(int)
        
    def __init__(self, *args, **kwargs):
        super(ViewerSlider, self).__init__(SliderWithViewer, *args, **kwargs)
        self.right_widget.valueChanged.connect(self.onValueChanged)
        
    def onValueChanged(self, v):
        self.valueChanged.emit(v)
        
    def setSync(self, b):
        self.right_widget.setSync(b)
        
    def setPrecise(self, f):
        self.right_widget.setPrecise(f)
        
    def setMaximumValue(self, v):
        self.right_widget.setMaximumValue(v)
        
    def setMinimumValue(self, v):
        self.right_widget.setMinimumValue(v)

    def setSliderMaximumValue(self, v):
        self.right_widget.setSliderMaximumValue(v)

    def setSliderMinimumValue(self, v):
        self.right_widget.setSliderMinimumValue(v)

    def setViewerMaximumValue(self, v):
        self.right_widget.setViewerMaximumValue(v)

    def setViewerMinimumValue(self, v):
        self.right_widget.setViewerMinimumValue(v)
        
    def setValue(self, v):
        self.right_widget.setValue(v)
        
    def getValue(self):
        return self.right_widget.getValue()
    
    def getSliderValue(self):
        return self.right_widget.getSliderValue()
    
    def getViewerValue(self):
        return self.right_widget.getViewerValue()