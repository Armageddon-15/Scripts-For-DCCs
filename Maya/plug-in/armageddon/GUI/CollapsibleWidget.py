from PySide2.QtWidgets import QToolButton, QWidget, QScrollArea, QSizePolicy, QFrame, QVBoxLayout
from PySide2.QtCore import Qt, QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation


class CollapsibleHeader(QWidget):
    def __init__(self, parent=None, header_title="", block_widget=None, header_font_size=15, *args, **kwargs):
        super(CollapsibleHeader, self).__init__(parent, *args, **kwargs)
        
        self.content_height_hint = 0
                
        self.header = QToolButton(self)
        font = self.header.font()
        font.setBold(True) 
        font.setPointSize(header_font_size)
        self.header.setFont(font)
        self.header.setText(header_title)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        self.header.setSizePolicy(sizePolicy)
        # self.header.
        self.header.setCheckable(True)
        self.header.setChecked(True)
        self.header.setStyleSheet("QToolButton{border: 0.5px solid gray; border-radius: 3px}")
        self.header.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.header.setArrowType(Qt.RightArrow)
        self.header.pressed.connect(self.clickCollapse)
        
        self.block_widget = QWidget(self)
        self.block_vbox = QVBoxLayout(self.block_widget)
        self.block_vbox.setContentsMargins(10,0,0,0)
        if block_widget is not None:
            self.addWidget(block_widget)
        
        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(1)
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.addWidget(self.header)
        self.vbox.addWidget(self.block_widget)
        
        self.clickCollapse()
        
    
    def clickCollapse(self):
        checked = self.header.isChecked()
        if checked:
            self.header.setArrowType(Qt.DownArrow)
            self.block_widget.setMaximumHeight(self.content_height_hint)
        else:
            self.header.setArrowType(Qt.RightArrow)
            self.block_widget.setMaximumHeight(0)
        
        
    def addWidget(self, widget):
        self.block_vbox.addWidget(widget)
        self.content_height_hint = self.block_widget.sizeHint().height()
        
    def setHeaderFont(self, font): 
        self.header.setFont(font)
        
    def setHeaderBold(self, is_bold):
        font = self.header.font()
        font.setBold(is_bold)         
    
    def setBlockItemSpacing(self, spacing):
        self.block_vbox.setSpacing(spacing)
    
    def setSpacing(self, spacing):
        self.vbox.setSpacing(spacing)     
           
    def setBlockItemContentsMargins(self, *args, **kwargs):
        self.block_vbox.setContentsMargins(*args, **kwargs)
    
    def setContentsMargins(self, *args, **kwargs):
        self.vbox.setContentsMargins(*args, **kwargs)    
        
    
class CollapsibleBox(QWidget):
    def __init__(self, parent=None, title="", *args, **kwargs):
        super(CollapsibleBox, self).__init__(parent, *args, **kwargs)

        self.toggle_button = QToolButton(
            text=title, checkable=True, checked=False
        )
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        self.toggle_animation = QParallelAnimationGroup(self)

        self.content_area = QScrollArea(
            maximumHeight=0, minimumHeight=0
        )
        self.content_area.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )
        self.content_area.setFrameShape(QFrame.NoFrame)

        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

        self.toggle_animation.addAnimation(
            QPropertyAnimation(self, b"minimumHeight")
        )
        self.toggle_animation.addAnimation(
            QPropertyAnimation(self, b"maximumHeight")
        )
        self.toggle_animation.addAnimation(
            QPropertyAnimation(self.content_area, b"maximumHeight")
        )

    def on_pressed(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(
            Qt.DownArrow if not checked else Qt.RightArrow
        )
        self.toggle_animation.setDirection(
            QAbstractAnimation.Forward
            if not checked
            else QAbstractAnimation.Backward
        )
        self.toggle_animation.start()

    def setContentLayout(self, layout):
        lay = self.content_area.layout()
        del lay
        self.content_area.setLayout(layout)
        collapsed_height = (
            self.sizeHint().height() - self.content_area.maximumHeight()
        )
        content_height = layout.sizeHint().height()
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(500)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(500)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)
