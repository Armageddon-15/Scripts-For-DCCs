import mset
import MatchHiLowToBakerBackend as Backend


class MatchHiLowToBaker:
    main_window = mset.UIWindow("Match Hi Low To Baker")
    start_drawer = mset.UIDrawer("Start")
    start_window = mset.UIWindow("Start Win")
    fin_drawer = mset.UIDrawer("Finish")
    fin_window = mset.UIWindow("Finish Win")

    def __init__(self):
        self.high_suffix = mset.UITextField()
        self.low_suffix = mset.UITextField()

        self.match_all_btn = mset.UIButton("Match All")
        self.match_select_btn = mset.UIButton("Match Selection")

        self.no_match_creation_cbox = mset.UICheckBox("Create if Low Exist")

        self.bake_all_btn = mset.UIButton("Bake All")
        self.bake_select_btn = mset.UIButton("Bake Selection")

        self.initStartDrawer()
        self.initFinDrawer()

    def show(self):
        self.start_window.addElement(mset.UILabel("High Poly Suffix: "))
        self.start_window.addElement(self.high_suffix)
        self.start_window.addReturn()
        self.start_window.addElement(mset.UILabel("Low Poly Suffix: "))
        self.start_window.addElement(self.low_suffix)
        self.start_window.addReturn()
        self.start_window.addElement(self.match_all_btn)
        self.start_window.addStretchSpace()
        self.start_window.addElement(self.match_select_btn)
        self.start_window.addReturn()
        self.start_window.addElement(self.no_match_creation_cbox)
        self.main_window.addElement(self.start_drawer)
        self.main_window.addReturn()
        self.fin_window.addElement(self.bake_all_btn)
        self.fin_window.addStretchSpace()
        self.fin_window.addElement(self.bake_select_btn)
        self.main_window.addElement(self.fin_drawer)

    def initStartDrawer(self):
        self.start_drawer.containedControl = self.start_window
        self.high_suffix.value = "_hi"
        self.low_suffix.value = "_low"
        self.match_all_btn.onClick = self.matchAll
        self.match_select_btn.onClick = self.matchSelection

    def initFinDrawer(self):
        self.fin_drawer.containedControl = self.fin_window

    def apply(self):
        Backend.setSetting(self.low_suffix.value, self.high_suffix.value)
        Backend.matchingNames(self.no_match_creation_cbox.value)

    def matchAll(self):
        Backend.getAllExternalObj()
        self.apply()

    def matchSelection(self):
        Backend.getSelectedExternalObj()
        self.apply()


def main():
    window = MatchHiLowToBaker()
    window.show()
