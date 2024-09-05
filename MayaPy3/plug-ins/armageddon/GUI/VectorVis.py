from PySide2.QtWidgets import QWidget, QSlider, QDoubleSpinBox, QHBoxLayout, QAbstractSpinBox
from PySide2.QtCore import Signal, Slot, Qt

class Vector3SpinBox(QWidget):
    def __init__(self, *args, **kwargs):
        super(Vector3SpinBox, self).__init__(*args, **kwargs)
        self.x_spin = QDoubleSpinBox(self)
        self.y_spin = QDoubleSpinBox(self)
        self.z_spin = QDoubleSpinBox(self)
        self.spins = [self.x_spin, self.y_spin, self.z_spin]
        
        self.hbox = QHBoxLayout(self)
        self.hbox.setContentsMargins(0,0,0,0)
        for spin in self.spins:
            spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            self.hbox.addWidget(spin)
            
    def setMinimumValue(self, v, index=-1):
        if not index < 0:
            self.spins[index].setMinimum(v)
            return None
        
        for i in range(3):
            self.spins[i].setMinimum(v)
            
    def setMaximumValue(self, v, index=-1):
        if not index < 0:
            self.spins[index].setMaximum(v)
            return None
        
        for i in range(3):
            self.spins[i].setMaximum(v)            
            
    def setMinMax(self, min_v, max_v, index=-1):
        self.setMinimumValue(min_v, index)
        self.setMaximumValue(max_v, index)
        
    def setVisMinimumSize(self, *args, **kwargs):
        for i in range(3):
            self.spins[i].setMinimumSize(*args, **kwargs)         
        
    def setVisMaximumSize(self, *args, **kwargs):
        for i in range(3):
            self.spins[i].setMaximumSize(*args, **kwargs)          
        
    def setVisMinimumWidth(self, *args, **kwargs):
        for i in range(3):
            self.spins[i].setMinimumWidth(*args, **kwargs)         
        
    def setVisMaximumWidth(self, *args, **kwargs):
        for i in range(3):
            self.spins[i].setMaximumWidth(*args, **kwargs)
            
    def setVisMinimumHeight(self, *args, **kwargs):
        for i in range(3):
            self.spins[i].setMinimumHeight(*args, **kwargs)         
        
    def setVisMaximumHeight(self, *args, **kwargs):
        for i in range(3):
            self.spins[i].setMaximumHeight(*args, **kwargs)            
            
    def setValue(self, v, index=-1):
        if index < 0:
            for i in range(3):        
                if type(v) is list: 
                    self.spins[i].setValue(v[i])
                else:
                    self.spins[i].setValue(v)
            return None
        
        self.spins[index].setValue(v)
        return None
            
    def setX(self, v):
        self.x_spin.setValue(v)
            
    def setY(self, v):
        self.y_spin.setValue(v)        
        
    def setZ(self, v):
        self.z_spin.setValue(v)
        
    def getX(self):
        return self.x_spin.value()
        
    def getY(self):
        return self.y_spin.value()    
        
    def getZ(self):
        return self.z_spin.value()    
    
    def getVector(self):
        return [self.getX(), self.getY(), self.getZ()]
    
    
    