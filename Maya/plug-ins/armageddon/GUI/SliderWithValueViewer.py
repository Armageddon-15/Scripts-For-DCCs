from PySide2.QtWidgets import QWidget, QSlider, QDoubleSpinBox, QHBoxLayout, QAbstractSpinBox
from PySide2.QtCore import Signal, Slot, Qt

class SliderWithViewer(QWidget):
    # sliderMoved = Signal(int)
    valueChanged = Signal(float)
    
    def __init__(self, parent=None, sync_min_max=True, scale_precise=0.01, *args, **kwargs):
        super(SliderWithViewer, self).__init__(parent, *args, **kwargs)
        self.sync_min_max = sync_min_max
        self.scale_precise = scale_precise
        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Horizontal)
        self.viewer = QDoubleSpinBox(self)
        self.viewer.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.viewer.stepBy(0.1)
        
        self.slider.valueChanged.connect(self.changeViewerValue)
        self.viewer.editingFinished.connect(self.changeSliderValue)
        
        if self.sync_min_max:
            self.viewer.setMaximum(self.slider.maximum()/self.scale_precise)
            
        self.hbox = QHBoxLayout(self)
        self.hbox.setContentsMargins(0,0,0,0)
        self.hbox.setSpacing(1)
        self.hbox.addWidget(self.slider)
        self.hbox.addWidget(self.viewer)
        
    def changeSliderValue(self):
        v = self.viewer.value()/self.scale_precise
        self.slider.setValue(v)
        self.valueChanged.emit(v)
        
    @Slot(int)        
    def changeViewerValue(self, v):
        self.viewer.setValue(v*self.scale_precise)
        self.valueChanged.emit(v*self.scale_precise)
        
    def setSync(self, b):
        self.sync_min_max = b
        
    def setPrecise(self, f):
        self.scale_precise = f
        
    def setMaximumValue(self, v):
        if self.sync_min_max:
            self.viewer.setMaximum(v)
            self.slider.setMaximum(v/self.scale_precise)
        
    def setMinimumValue(self, v):
        if self.sync_min_max:
            self.viewer.setMinimum(v)
            self.slider.setMinimum(v/self.scale_precise)

    def setSliderMaximumValue(self, v):
        self.slider.setMaximum(v/self.scale_precise)
        if self.sync_min_max:
            self.viewer.setMaximum(v)

    def setSliderMinimumValue(self, v):
        self.slider.setMinimum(v/self.scale_precise)
        if self.sync_min_max:
            self.viewer.setMinimum(v)

    def setViewerMaximumValue(self, v):
        self.viewer.setMaximum(v)
        if self.sync_min_max:
            self.slider.setMaximum(v/self.scale_precise)

    def setViewerMinimumValue(self, v):
        self.viewer.setMinimum(v)
        if self.sync_min_max:
            self.slider.setMinimum(v/self.scale_precise)
            
    def setValue(self, v):
        self.slider.setValue(v/self.scale_precise)
        self.viewer.setValue(v) 
        
    def getValue(self):
        return self.viewer.value()
    
    def getSliderValue(self):
        return self.slider.value()*self.scale_precise
    
    def getViewerValue(self):
        return self.viewer.value()
