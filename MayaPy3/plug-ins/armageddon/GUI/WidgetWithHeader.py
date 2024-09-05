from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout

class WidgetWithHeader(QWidget):
    def __init__(self, parent, header_text="", header_font_size=10, *args, **kwargs):
        super(WidgetWithHeader, self).__init__(parent, *args, **kwargs)
        
        self.header = QLabel(self)
        self.header.setText(header_text)
        font = self.header.font()
        font.setBold(True) 
        font.setPointSize(header_font_size)
        self.header.setFont(font)
        
        self.widget_block = QWidget(self)
        self.block_vbox = QVBoxLayout(self.widget_block)
        self.block_vbox.setContentsMargins(10, 0, 0, 0)
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
        
        self.main_vbox.addWidget(self.header)
        self.main_vbox.addWidget(self.widget_block)
        
    def addWidget(self, obj):
        self.block_vbox.addWidget(obj)
        
    def setHeaderFont(self, font): 
        self.header.setFont(font)
        
    def setHeaderBold(self, is_bold):
        font = self.header.font()
        font.setBold(is_bold)         
    
    def setBlockItemSpacing(self, spacing):
        self.block_vbox.setSpacing(spacing)
    
    def setSpacing(self, spacing):
        self.main_vbox.setSpacing(spacing)     
           
    def setBlockItemContentsMargins(self, *args, **kwargs):
        self.block_vbox.setContentsMargins(*args, **kwargs)
    
    def setContentsMargins(self, *args, **kwargs):
        self.main_vbox.setContentsMargins(*args, **kwargs)        