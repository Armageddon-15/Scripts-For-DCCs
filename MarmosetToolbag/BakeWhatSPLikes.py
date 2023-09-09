import mset
import BakeWhatSPLikesBackend as Backend


class BakeSubstancePainterTextureUI:
    main_window = mset.UIWindow("Bake SP Texture")
    main_window.width = 350
    setting_drawer = mset.UIDrawer("Settings")
    drawer_window = mset.UIWindow("Settings Window")
    maps_drawer = mset.UIDrawer("Maps")
    maps_drawer_window = mset.UIWindow("Maps Window")

    def __init__(self):

        self.using_check_boxes = [mset.UICheckBox()]*0

        self.select_all_btn = mset.UIButton("Select ALL Settings")
        self.deselect_all_btn = mset.UIButton("Deselect All Settings")
        self.select_all_btn.onClick = self.selectAllSettings
        self.deselect_all_btn.onClick = self.deselectAllSettings

        self.using_path_setting = mset.UICheckBox()
        self.path_text_field = mset.UITextField()
        self.path_btn = mset.UIButton()
        self.subfolder_checkbox = mset.UICheckBox("Use Subfolder")
        self.create_if_not_exist = mset.UICheckBox("Create Folder If Not Exist")
        self.initPathField()

        self.format_label = mset.UILabel("Image Format: ")
        self.format_list_box = mset.UIListBox()
        self.using_bit = mset.UICheckBox("Image Bit Per Channel: ")
        self.bit_list_box = mset.UIListBox()
        self.using_resolution = mset.UICheckBox("Image Size: ")
        self.resolution_field = mset.UITextFieldInt()

        self.wtf_label = mset.UILabel()
        self.wtf_label.text = "Cannot find where tooltips ui method and\nhanded orientation setting in baker are.\nBe sure all handed setting of\n" \
                              "bakers are same as below option"
        self.wtf_label.setMonospaced(True)
        self.handed_ori = mset.UIListBox()
        self.initSettingDrawer()

        self.maps_list = [mset.UICheckBox()] * 0
        self.using_map = mset.UICheckBox("Use Map Setting")
        self.initMapsDrawer()

        self.apply_all_btn = mset.UIButton("Apply To All")
        self.apply_select_btn = mset.UIButton("Apply To Selection")
        self.apply_all_btn.onClick = self.applyToAll
        self.apply_select_btn.onClick = self.applyToSelection

    def show(self):
        self.main_window.addElement(self.select_all_btn)
        self.main_window.addStretchSpace()
        self.main_window.addElement(self.deselect_all_btn)
        self.main_window.addReturn()
        self.main_window.addElement(mset.UILabel(" "))
        self.main_window.addReturn()
        self.main_window.addElement(self.using_path_setting)
        self.main_window.addElement(self.path_text_field)
        self.main_window.addElement(self.path_btn)
        self.main_window.addReturn()
        self.main_window.addSpace(20)
        self.main_window.addElement(self.subfolder_checkbox)
        self.main_window.addStretchSpace()
        self.main_window.addElement(self.create_if_not_exist)
        self.main_window.addReturn()

        self.drawer_window.addSpace(20)
        self.drawer_window.addElement(self.format_label)
        self.drawer_window.addElement(self.format_list_box)
        self.drawer_window.addReturn()
        self.drawer_window.addElement(self.using_bit)
        self.drawer_window.addElement(self.bit_list_box)
        self.drawer_window.addReturn()
        self.drawer_window.addElement(self.using_resolution)
        self.drawer_window.addElement(self.resolution_field)
        self.drawer_window.addReturn()
        self.drawer_window.addElement(mset.UILabel(" "))
        self.drawer_window.addReturn()
        self.drawer_window.addElement(self.wtf_label)
        self.drawer_window.addReturn()
        self.drawer_window.addElement(mset.UILabel("Tangent Orientation"))
        self.drawer_window.addElement(self.handed_ori)
        self.drawer_window.addReturn()
        self.main_window.addElement(self.setting_drawer)
        self.main_window.addReturn()

        self.maps_drawer_window.addElement(self.using_map)
        self.maps_drawer_window.addReturn()
        for cbox in self.maps_list:
            self.maps_drawer_window.addSpace(10)
            self.maps_drawer_window.addElement(cbox)
            self.maps_drawer_window.addReturn()

        self.main_window.addElement(self.maps_drawer)
        self.main_window.addReturn()

        self.main_window.addElement(self.apply_all_btn)
        self.main_window.addStretchSpace()
        self.main_window.addElement(self.apply_select_btn)

    def getPathToTTextField(self):
        path = mset.showOpenFolderDialog()
        if path is not None:
            self.path_text_field.value = path

    def initPathField(self):
        self.using_path_setting.value = True
        self.using_check_boxes.append(self.using_path_setting)

        self.subfolder_checkbox.value = True
        self.create_if_not_exist.value = True
        self.path_btn.text = "..."
        self.path_btn.onClick = self.getPathToTTextField

    def initSettingDrawer(self):
        self.setting_drawer.containedControl = self.drawer_window

        self.using_bit.value = True
        self.using_resolution.value = True
        self.using_check_boxes.extend([self.using_bit, self.using_resolution])

        for item in Backend.BAKE_FORMAT:
            self.format_list_box.addItem(item)
        self.format_list_box.selectedItem = 0

        for item in Backend.CHANNEL_BIT:
            self.bit_list_box.addItem(item)
        self.bit_list_box.selectedItem = 0

        self.resolution_field.value = 2048

        for item in Backend.HANDED_ORIENTATION:
            self.handed_ori.addItem(item)
        handed = mset.getPreferences().defaultTangentHandedness
        self.handed_ori.selectItemByName(handed)

    def initMapsDrawer(self):
        self.maps_drawer.containedControl = self.maps_drawer_window
        self.using_map.value = True
        self.using_check_boxes.append(self.using_map)
        for name in Backend.SP_BAKE_TEX_NAME:
            check_box = mset.UICheckBox(name)
            check_box.value = True
            self.maps_list.append(check_box)

    def selectAllSettings(self):
        for cbox in self.using_check_boxes:
            cbox.value = True

    def deselectAllSettings(self):
        for cbox in self.using_check_boxes:
            cbox.value = False

    def toBackendSettings(self):
        tex_setting = [True]*0
        for i in self.maps_list:
            tex_setting.append(i.value)

        Backend.setAllSettings(self.using_path_setting.value,
                               self.path_text_field.value,
                               self.subfolder_checkbox.value,
                               self.create_if_not_exist.value,
                               Backend.BAKE_FORMAT[self.format_list_box.selectedItem],
                               self.using_bit.value,
                               Backend.CHANNEL_BIT[self.bit_list_box.selectedItem],
                               self.using_resolution.value,
                               self.resolution_field.value,
                               Backend.HANDED_ORIENTATION[self.handed_ori.selectedItem],
                               self.using_map.value,
                               tex_setting
                               )

    def apply(self):
        self.toBackendSettings()
        Backend.setBakersAsSettingItems()

    def applyToAll(self):
        Backend.getAllBakers()
        self.apply()

    def applyToSelection(self):
        Backend.getSelectedBakers()
        self.apply()


def main():
    window = BakeSubstancePainterTextureUI()
    window.show()
