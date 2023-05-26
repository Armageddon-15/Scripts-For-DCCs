from PySide2.QtWidgets import QWidget, QFrame, QLabel, QLineEdit, QPushButton, QComboBox, QHBoxLayout, QVBoxLayout, QSizePolicy
# from PySide2.QtGui import QPalette, QColor
from PySide2.QtCore import Qt

import auto_fill_baked_texture_backend as backend

import substance_painter.ui as sp_ui
import substance_painter.logging as sp_logging

import sys
import os

_gui_instance = None


class Separator(QLabel):
    def __init__(self, parent=None):
        super(Separator, self).__init__(parent)
        self.setStyleSheet("QLabel {background-color: #3e3e3e; padding: 0; margin: 0; border-bottom: 1 solid #666; border-top: 1 solid #2a2a2a;}")
        self.setMaximumHeight(2)


class NameEditorWidget(QWidget):
    def __init__(self, parent=None, label_name: str = None, value: str = None):
        super(NameEditorWidget, self).__init__(parent)

        self.__name_label = QLabel(self)
        self.__name_value = QLineEdit(self)

        if type(label_name) is str:
            self.__name_label.setText(label_name)
        if type(value) is str:
            self.__name_value.setText(value)

        self.colon = QLabel(self)
        self.colon.setText(":")

        # self.texture_set_name.setPlaceholderText("Fill this text")

        self.hbox = QHBoxLayout(self)
        self.hbox.setContentsMargins(5, 1, 5, 1)
        self.hbox.addWidget(self.__name_label)
        self.hbox.addWidget(self.colon)
        self.hbox.addWidget(self.__name_value)

    @property
    def label_name(self):
        return self.__name_label.text()

    @label_name.setter
    def label_name(self, label_name: str):
        self.__name_label.setText(label_name)

    @property
    def value_string(self):
        return self.__name_value.text()

    @value_string.setter
    def value_string(self, value: str):
        self.__name_value.setText(value)

    def setReadOnly(self, b: bool):
        self.__name_value.setReadOnly(b)


class Combobox(QComboBox):
    def __init__(self, parent):
        super(Combobox, self).__init__(parent)
        self.main = parent

    def currentTextChanged(self, i: int):
        self.main.updatePreset(self.itemText(i))


class ComboboxEditorWidget(QWidget):
    def __init__(self, parent=None, label_name: str = None):
        super(ComboboxEditorWidget, self).__init__(parent)
        self.main = parent
        self.__name_label = QLabel(self)
        self.dropdown_box = QComboBox(self)
        self.dropdown_box.currentIndexChanged.connect(self.updatePreset)
        self.dropdown_box.currentTextChanged.connect(self.updateButton)
        self.dropdown_box.setMinimumWidth(200)
        self.dropdown_box.setDuplicatesEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        self.dropdown_box.setSizePolicy(sizePolicy)
        self.dropdown_box.setEditable(True)

        if type(label_name) is str:
            self.__name_label.setText(label_name)

        self.colon = QLabel(self)
        self.colon.setText(":")

        # self.texture_set_name.setPlaceholderText("Fill this text")

        self.hbox = QHBoxLayout(self)
        self.hbox.addWidget(self.__name_label)
        self.hbox.addWidget(self.colon)
        self.hbox.addWidget(self.dropdown_box)
        self.hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)

    @property
    def label_name(self):
        return self.__name_label.text()

    @label_name.setter
    def label_name(self, label_name: str):
        self.__name_label.setText(label_name)

    def currentText(self):
        return self.dropdown_box.currentText()

    def removeCurrentItem(self):
        self.dropdown_box.removeItem(self.dropdown_box.currentIndex())

    def setEditable(self, b: bool):
        self.dropdown_box.setEditable(b)

    def setComboboxList(self, items: list):
        self.dropdown_box.addItems(items)

    def updatePreset(self, i: int):
        self.main.updatePreset(self.dropdown_box.itemText(i))

    def updateButton(self, text: str):
        self.main.updateButton(text)


class PresetWidget(QWidget):
    def __init__(self, parent):
        super(PresetWidget, self).__init__(parent)
        self.main = parent

        self.preset_dropbox = ComboboxEditorWidget(self, "Preset")

        self.save_btn = QPushButton(self)
        self.save_btn.setText("Save")
        self.save_btn.clicked.connect(self.savePreset)
        self.delete_btn = QPushButton(self)
        self.delete_btn.setText("Delete")
        self.delete_btn.clicked.connect(self.deletePreset)
        self.btn_frame = QFrame(self)

        self.preset_dropbox.setComboboxList(backend.getAllPresetsData())

        self.frame_hbox = QHBoxLayout(self.btn_frame)
        self.frame_hbox.setContentsMargins(5, 0, 5, 0)
        self.frame_hbox.addWidget(self.save_btn)
        self.frame_hbox.addWidget(self.delete_btn)

        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 2, 0, 2)
        self.vbox.addWidget(self.preset_dropbox)
        self.vbox.addWidget(self.btn_frame)

    def savePreset(self):
        name = self.preset_dropbox.currentText()
        self.main.savePreset(name)
        if self.preset_dropbox.dropdown_box.findText(name) == -1:
            self.preset_dropbox.dropdown_box.addItem(name)
        self.updatePreset(self.preset_dropbox.currentText())

    def deletePreset(self):
        if self.preset_dropbox.currentText() != "Default":
            backend.deletePresetData(self.preset_dropbox.currentText())
            self.preset_dropbox.removeCurrentItem()
            self.main.deletePreset()
            self.updatePreset(self.preset_dropbox.currentText())

    def updatePreset(self, name: str):
        self.main.updatePreset(name)

    def updateButton(self, name):
        if name != "Default":
            self.save_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
        else:
            self.save_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)


class SuffixWidget(QWidget):
    def __init__(self, parent=None):
        super(SuffixWidget, self).__init__(parent)
        self.main = parent
        self.settings = [NameEditorWidget()]
        self.settings.clear()
        self.suffix_title = QLabel(self)
        self.suffix_title.setText("Suffix: ")

        self.apply_btn = QPushButton(self)
        self.apply_btn.clicked.connect(self.applyClicked)
        self.apply_btn.setText("Apply")
        self.apply_btn.setMaximumWidth(200)

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(4)
        self.vbox.addWidget(self.suffix_title)

        for i in range(len(backend.texture_set_list)):
            self.settings.append(NameEditorWidget(self))
            self.settings[i].label_name = backend.texture_set_list[i]
            # sp_logging.info(self.settings[i].label_name)

            self.vbox.addWidget(self.settings[i])
        # self.vbox.addWidget(self.settings[1])

        self.vbox.addWidget(self.apply_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

    def getAllSuffixes(self) -> dict:
        result = {}
        for editor in self.settings:
            result.update({editor.label_name: editor.value_string})

        return result

    def setSuffix(self, label: str, value: str):
        self.settings[backend.texture_set_list.index(label)].value_string = value

    def setAllSuffixes(self, d: dict):
        for editor in self.settings:
            editor.value_string = d[editor.label_name]

    def clearAll(self):
        for editor in self.settings:
            editor.value_string = ""

    def applyClicked(self):
        self.main.toTextureSet()


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Fill Texture Set")
        self.prefix_editor = NameEditorWidget(self, "Prefix Name")
        self.separator = Separator(self)

        self.suffix_widget = SuffixWidget(self)
        self.suffix_widget.setAllSuffixes(backend.getDefaultPreset())

        self.preset_widget = PresetWidget(self)

        self.expanding_frame = QFrame(self)
        # self.expanding_frame.setStyleSheet("background_color:rgb(0,0,0)")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        self.expanding_frame.setSizePolicy(sizePolicy)

        self.separator2 = Separator(self)
        self.json_filename_editor = NameEditorWidget(self, "Json File Path")
        self.json_filename_editor.value_string = backend.json_path
        self.json_filename_editor.setReadOnly(True)

        # self.reload_json_btn = QPushButton(self)
        # self.reload_json_btn.setText("Reload Json File")

        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.prefix_editor)
        self.vbox.addWidget(self.separator)
        self.vbox.addWidget(self.preset_widget)
        self.vbox.addWidget(self.suffix_widget)
        self.vbox.addWidget(self.expanding_frame)
        self.vbox.addWidget(self.separator2)
        self.vbox.addWidget(self.json_filename_editor)
        # self.vbox.addWidget(self.reload_json_btn)

    def savePreset(self, name: str):
        suffix_dict = self.suffix_widget.getAllSuffixes()
        suffix_dict.update({"Name": name})
        backend.savePresetData(suffix_dict)

    def deletePreset(self):
        self.suffix_widget.clearAll()

    def updatePreset(self, name: str):
        self.suffix_widget.setAllSuffixes(backend.getPreset(name))

    def toTextureSet(self):
        suffixes = self.suffix_widget.getAllSuffixes()
        for key in suffixes.keys():
            suffixes.update({key: self.prefix_editor.value_string + suffixes[key]})

        backend.applyAllTextureToTextureSet(backend.getActiveTextureSet(), suffixes)


def start_plugin():
    backend.loadJsonData()
    global _gui_instance
    _gui_instance = MainWindow()
    sp_ui.add_dock_widget(_gui_instance)
    # sp_logging.info(_json_path)


def close_plugin():
    global _gui_instance
    sp_ui.delete_ui_element(_gui_instance)
    del _gui_instance
