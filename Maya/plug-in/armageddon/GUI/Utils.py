# -*- coding: UTF-8 -*-

from PySide2.QtWidgets import QPushButton


def addButton(obj, text="", tool_tip=""):
    btn = QPushButton(obj)
    btn.setText(text)
    btn.setToolTip(tool_tip)
    return btn


def addWidget(obj, widget_class, text="", tool_tip=""):
    widget = widget_class(obj)
    widget.setText(text)
    widget.setToolTip(tool_tip)
    return widget