# -*- coding: UTF-8 -*-

from PySide2.QtWidgets import QPushButton
from typing import Type, TypeVar

T = TypeVar("T")


def addButton(obj, text="", tool_tip=""):
    btn = QPushButton(obj)
    btn.setText(text)
    btn.setToolTip(tool_tip)
    return btn


def addWidget(obj, widget_class: Type[T], text="", tool_tip="") -> T:
    widget = widget_class(obj)
    widget.setText(text)
    widget.setToolTip(tool_tip)
    return widget