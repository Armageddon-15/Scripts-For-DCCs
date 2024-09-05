from PySide2.QtWidgets import QFrame


class Separator(QFrame):
    def __init__(self, parent=None, minimum_height=20, *args, **kwargs):
        super(Separator, self).__init__(parent, *args, **kwargs)
        self.setFrameShape(QFrame.HLine)
        self.setMinimumSize(0, minimum_height)