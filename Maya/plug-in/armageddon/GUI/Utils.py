# -*- coding: UTF-8 -*-

from PySide2.QtWidgets import QPushButton


def addButton(obj, text, tool_tip):
    btn = QPushButton(obj)
    btn.setText(text)
    btn.setToolTip(tool_tip)
    return btn


def addWidget(obj, text, tool_tip, widget_class):
    widget = widget_class(obj)
    widget.setText(text)
    widget.setToolTip(tool_tip)
    return widget