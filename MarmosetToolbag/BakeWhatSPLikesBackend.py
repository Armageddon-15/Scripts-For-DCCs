from typing import Any, List, Tuple, Callable, Union
import mset
import os
import Utils

BAKE_FORMAT = [".png", ".psd", ".tga", ".jpg"]
CHANNEL_BIT = ["8", "16", "32"]
HANDED_ORIENTATION = ["Right-Handed", "Left-Handed"]

SP_BAKE_ID = [0, 1, 25, 10, 4, 3, 7, 2, 8, 30]
SP_BAKE_TEX_NAME = ["Normals", "Normals(Object)", "Material ID", "Ambient Occlusion",
                    "Curvature", "Position", "Thickness", "Height", "BentNormal", "Opacity"]

bakers: List[mset.BakerObject] = []


class Settings:
    using_path          = False
    prefix_path         = ""
    using_subfolder     = True
    create_if_not_exist = True
    extension           = ""
    using_bit           = False
    output_bit          = 8
    using_res           = False
    res                 = 2048
    tangent_handed      = "Left-Handed"
    using_map           = False
    maps_settings       = [True] * 10


def setAllSettings(using_path: bool, prefix_path: str, using_subfolder: bool, create_if_not_exist: bool,
                   extension: str, using_bit: bool, output_bit: str, using_res: bool,
                   res: int, tangent_handed: str, using_map: bool, maps_settings: List[bool]):
    Settings.using_path             = using_path
    Settings.prefix_path            = prefix_path
    Settings.using_subfolder        = using_subfolder
    Settings.create_if_not_exist    = create_if_not_exist
    Settings.extension              = extension
    Settings.using_bit              = using_bit
    Settings.output_bit             = int(output_bit)
    Settings.using_res              = using_res
    Settings.res                    = res
    Settings.tangent_handed         = tangent_handed
    Settings.using_map              = using_map
    Settings.maps_settings          = maps_settings

    # for it in Settings.__dict__:
    #     print(it, Settings.__dict__[it])


def __getBakers(fun):
    baker_objects = Utils.getCertainTypeWithCertainFunc(fun, mset.BakerObject)
    return baker_objects


def getAllBakers():
    global bakers
    bakers = __getBakers(mset.getAllObjects)


def getSelectedBakers():
    global bakers
    bakers = __getBakers(mset.getSelectedObjects)


def __setBakerAsSettingItems(baker: mset.BakerObject):
    # filename setting
    print("filename setting")
    if Settings.using_path and Settings.prefix_path != "":
        name = baker.name
        if Settings.using_subfolder:
            path = os.path.join(Settings.prefix_path, name)
        else:
            path = Settings.prefix_path
        if Settings.create_if_not_exist:
            Utils.makeDir(path)
        filename = os.path.join(path, name) + Settings.extension
        filename = filename.replace("\\", "/")
        print("A")
        baker.outputPath = filename

    print("B")
    # image bit setting
    print("bit")
    if Settings.using_bit:
        baker.outputBits = Settings.output_bit

    # res setting
    print("res")
    if Settings.using_res:
        baker.outputWidth = Settings.res
        baker.outputHeight = Settings.res

    # maps setting
    maps = baker.getAllMaps()

    print("Map settings")
    if not Settings.using_map:
        return
    i = 0
    for index in SP_BAKE_ID:
        bake_map = maps[index]
        bake_map.enabled = Settings.maps_settings[i]
        print(bake_map.suffix, bake_map.enabled)
        if type(bake_map) is mset.NormalBakerMap:
            bake_map.flipY = (Settings.tangent_handed == HANDED_ORIENTATION[0])

        i += 1


def setBakersAsSettingItems():
    global bakers
    for baker in bakers:
        __setBakerAsSettingItems(baker)
