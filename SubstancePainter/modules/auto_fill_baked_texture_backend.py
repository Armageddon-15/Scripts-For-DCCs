import json
import os

import substance_painter.textureset as sp_ts
import substance_painter.resource as sp_resource
import substance_painter.logging as sp_logging


texture_set_list = ["Normal", "WorldSpaceNormal", "ID", "AO", "Curvature",
                    "Position", "Thickness", "Height", "BentNormals", "Opacity"]

default_preset = {"Name": "Default",
                  "Normal": "_normal",
                  "WorldSpaceNormal": "_normalobj",
                  "ID": "_id",
                  "AO": "_ao",
                  "Curvature": "_curve",
                  "Position": "_position",
                  "Thickness": "_thickness",
                  "Height": "_height",
                  "BentNormals": "_bentnormal",
                  "Opacity": "_opacity"}

json_path = os.path.join(os.path.abspath(os.path.dirname(__file__) + "\\..\\modules"), "auto_fill_baked_textures_settings.json")

_json_file = {}
_preset_data = {}


def loadJsonData():
    global _json_file
    if len(_json_file) == 0:
        if not os.path.exists(json_path):
            with open(json_path, "x", encoding='utf-8-sig') as file:
                temp_json_data = [default_preset]
                json.dump(temp_json_data, file, indent=4, ensure_ascii=False)

        with open(json_path, "r+", encoding='utf-8-sig') as file:
            _json_file = json.load(file)

        for data in _json_file:
            _preset_data.update({data["Name"]: data})


def savePresetData(data: dict):
    global _json_file
    _preset_data.update({data["Name"]: data})
    _preset_data.update({"Default": getDefaultPreset()})

    temp_preset = []
    for key in _preset_data:
        temp_preset.append(_preset_data[key])

    with open(json_path, "w", encoding='utf-8-sig') as file:
        json.dump(temp_preset, file, indent=4, ensure_ascii=False)

    _json_file = temp_preset


def deletePresetData(name: str):
    global _json_file
    _preset_data.pop(name)
    _preset_data.update({"Default": getDefaultPreset()})

    temp_preset = []
    for key in _preset_data:
        temp_preset.append(_preset_data[key])

    with open(json_path, "w", encoding='utf-8-sig') as file:
        json.dump(temp_preset, file, indent=4, ensure_ascii=False)

    _json_file = temp_preset


def getAllPresetsData():
    return _preset_data


def getAllPresetName():
    return _preset_data.keys()


def getPreset(name: str):
    return _preset_data[name]


def getDefaultPreset():
    return default_preset


def getActiveTextureSet():
    return sp_ts.get_active_stack().material()


def getMeshMapUsage(usage: str):
    try:
        u = getattr(sp_ts.MeshMapUsage, usage)
    except AttributeError:
        sp_logging.error(f"Cannot find Mesh Map: {usage}")
        return None
    return u


def getProjectResourceIDByName(name: str):
    return sp_resource.ResourceID.from_url(r"resource://project0/" + name)


def applyTextureToTextureSet(texture_set: sp_ts.TextureSet, usage: sp_ts.MeshMapUsage, mesh_map: sp_resource.ResourceID):
    texture_set.set_mesh_map_resource(usage, mesh_map)


def applyAllTextureToTextureSet(texture_set: sp_ts.TextureSet, d: dict):
    for key in d.keys():
        try:
            applyTextureToTextureSet(texture_set, getMeshMapUsage(key), getProjectResourceIDByName(d[key]))
        except Exception as e:
            sp_logging.warning(f"No Resource named {d[key]}, error: {e}")


if __name__ == '__main__':
    print(json_path)
    loadJsonData()