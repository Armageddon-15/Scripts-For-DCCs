from . import Parameters

from .GUI import CollapsibleWidget
from .Translate import TranslatorManager
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from .GUI.MayaMainWindow import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import os
import importlib

if not "main_ui" in globals():
    main_ui = None


class ItemWidget(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(ItemWidget, self).__init__(parent, *args, **kwargs)
        if parent is None:
            setWidgetAsMayaMainWindow(self, Parameters.MAIN_WIDGET_TITLE_NAME, Parameters.MAIN_WIDGET_OBJECT_NAME)

        # 0 - scroll
        # 1 - tab
        self.current_layout = 0

        self.widgets = []
        self.panel_list = []
        modules = packageCheck()

        for mod in modules:
            widget = mod.createWidget(self)
            self.widgets.append(widget)
            c_widget = CollapsibleWidget.CollapsibleHeader(self, mod.WIDGET_TITLE_NAME, widget)
            TranslatorManager.getTranslator().addTranslate(c_widget.header.setText, mod.WIDGET_TITLE_NAME)
            self.panel_list.append(c_widget)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setMovable(True)
        self.tab_widget.hide()

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.horizontalScrollBar().setEnabled(False)
        self.scroll_area.horizontalScrollBar().hide()
        self.scroll_area.setFrameStyle(0)
        self.scroll_widget = QWidget(self)
        self.scroll_vbox = QVBoxLayout(self.scroll_widget)
        self.scroll_vbox.setContentsMargins(1,1,1,1)
        self.scroll_vbox.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)

        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(1,1,1,1)
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.addWidget(self.scroll_area)

        self.switchToScroll()
        # self.vbox.addWidget(self.modeling_collapsible_header)

    @staticmethod
    def removeBoxItems(box):
        for i in reversed(range(0, box.count())):
            # box.itemAt(i).widget().hide()
            box.removeWidget(box.itemAt(i).widget())

    def switchToTab(self):
        self.tab_widget.clear()
        self.removeBoxItems(self.scroll_vbox)
        for panel in self.panel_list:
            self.tab_widget.addTab(panel, panel.getHeaderName())

        self.removeBoxItems(self.vbox)
        self.vbox.addWidget(self.tab_widget)

        self.tab_widget.show()
        self.scroll_area.hide()

        self.current_layout = 1

    def switchToScroll(self):
        self.tab_widget.clear()
        self.removeBoxItems(self.scroll_vbox)

        self.tab_widget.hide()
        self.scroll_area.show()
        for panel in self.panel_list:
            panel.show()
            self.scroll_vbox.addWidget(panel)

        self.removeBoxItems(self.vbox)
        self.vbox.addWidget(self.scroll_area)
        self.scroll_area.setMinimumWidth(max(self.scroll_area.minimumWidth(), self.scroll_widget.sizeHint().width()+10))
        self.current_layout = 0


class MainWindow(MayaQWidgetDockableMixin, QMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        super(MainWindow, self).__init__(parent, *args, **kwargs)
        if parent is None:
            setWidgetAsMayaMainWindow(self, Parameters.MAIN_WIDGET_TITLE_NAME, Parameters.MAIN_WIDGET_OBJECT_NAME)
        else:
            setWidgetName(self, Parameters.MAIN_WIDGET_TITLE_NAME, Parameters.MAIN_WIDGET_OBJECT_NAME)

        self.central_widget = None
        self.addSettingsMenu()
        self.addLanguageMenu()

    def addSettingsMenu(self):
        setting_menu = QMenu(self)
        TranslatorManager.getTranslator().addTranslate(setting_menu.setTitle, "Settings")
        self.menuBar().addMenu(setting_menu)
        switch_action = QAction(self)
        TranslatorManager.getTranslator().addTranslate(switch_action.setText, "Switch Layout")
        switch_action.triggered.connect(self.switchLayout)
        setting_menu.addAction(switch_action)

    def addLanguageMenu(self):
        setting_menu = QMenu(self)
        TranslatorManager.getTranslator().addTranslate(setting_menu.setTitle, "Language")
        self.menuBar().addMenu(setting_menu)
        switch_action = QAction(self)
        TranslatorManager.getTranslator().addTranslate(switch_action.setText, "Switch Language")
        switch_action.triggered.connect(self.switchLanguage)
        setting_menu.addAction(switch_action)

    def setMainWindow(self, widget_type):
        self.central_widget = widget_type(self)
        self.setCentralWidget(self.central_widget)


    def switchLayout(self):
        if type(self.central_widget) is not ItemWidget:
            return
        if self.central_widget.current_layout == 0:
            self.central_widget.switchToTab()
        elif self.central_widget.current_layout == 1:
            self.central_widget.switchToScroll()

    def switchLanguage(self):
        TranslatorManager.switchLanguage()
        if self.central_widget.current_layout == 1:
            self.central_widget.switchToTab()




def packageCheck():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_pack = os.path.basename(current_dir)
    modules = []
    module_dict = {}
    default_mods = []
    for file in os.listdir(current_dir):
        filename, ext = os.path.splitext(file)
        if ext != ".py":
            continue
        module_name = filename
        if not os.path.exists(os.path.join(current_dir, module_name + "Function.py")):
            continue
        # print(f"Trying to import {module_name}")
        try:
            mod = importlib.import_module("." + module_name, package=root_pack)
            modules.append(mod)
        except Exception as e:
            print(f"Failed to import {module_name}: {e}")
            continue
        # print(f"import {module_name} successfully")

        try:
            priority = mod.PRIORITY
        except Exception as e:
            default_mods.append(mod)
        else:
            if priority not in module_dict.keys():
                module_dict.update({priority: [mod]})
            else:
                module_dict[priority].append(mod)

    sorted_dict = sorted(module_dict.items())
    sort_mods = []
    for _, item in sorted_dict:
        sort_mods.extend(item)
    sort_mods.extend(default_mods)
    return sort_mods


def DockableWidgetUIScript():
    global main_ui
    TranslatorManager.resetTranslator()
    main_ui = MainWindow(getMayaMainWindow())
    main_ui.setMainWindow(ItemWidget)
    main_ui.show(dockable=True)
    main_ui.switchLayout()
    return main_ui


def show():
    print("\n====Start Armageddon Main Window=====\n")
    ui = DockableWidgetUIScript()
    return ui


if __name__ == '__main__':
    show()