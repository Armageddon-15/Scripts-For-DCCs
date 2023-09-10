from typing import List, Dict
import mset
import Utils


external_objs: List[mset.ExternalObject] = []


class Setting:
    high_poly_suffix = "_hi"
    low_poly_suffix = "_low"


def polyToNewBaker(hi_poly, low_poly, name=""):
    baker = mset.BakerObject()
    baker.name = name
    baker.addGroup(name)
    baker_group = baker.getChildren()[0]
    high, low = baker_group.getChildren()
    if low_poly is not None:
        low_poly.parent = low
    if hi_poly is not None:
        hi_poly.parent = high


def matchingNames(create_if_low_exist: bool):
    hi_objs = []
    low_objs = []
    mismatch_objs = []
    global external_objs

    for obj in external_objs:
        name = obj.name
        hi_index = name.find(Setting.high_poly_suffix)
        low_index = name.find(Setting.low_poly_suffix)
        if hi_index != -1 and low_index == -1:
            hi_objs.append(obj)
        elif hi_index == -1 and low_index != -1:
            low_objs.append(obj)
        else:
            mismatch_objs.append(obj)

    empty_low = []

    low_matched_hi: Dict[str, List[mset.ExternalObject]] = {}
    hi_matched_low: Dict[str, List[mset.ExternalObject]] = {}
    for low_obj in low_objs:
        low_matched_hi.update({low_obj.name: []})
        for hi_obj in hi_objs:
            if low_obj.name.find(hi_obj.name.split(Setting.high_poly_suffix)[0]) != -1:
                low_matched_hi[low_obj.name].append(hi_obj)
            if hi_obj.name.find(low_obj.name.split(Setting.low_poly_suffix)[0]) != -1:
                if hi_obj.name in hi_matched_low:
                    hi_matched_low[hi_obj.name].append(low_obj)
                else:
                    hi_matched_low.update({hi_obj.name: [low_obj]})
        if len(low_matched_hi[low_obj.name]) == 0:
            empty_low.append(low_obj)
    if create_if_low_exist:
        for low_obj in empty_low:
            polyToNewBaker(None, low_obj, low_obj.name.split(Setting.low_poly_suffix)[0])

    # print(low_matched_hi)
    # print(hi_matched_low)
    for low in low_matched_hi:
        for matched_hi in low_matched_hi[low]:
            if matched_hi.name in hi_matched_low:
                for matched_low in hi_matched_low[matched_hi.name]:
                    if matched_low.name in low_matched_hi:
                        name = matched_low.name.split(Setting.low_poly_suffix)[0]
                        polyToNewBaker(matched_hi, matched_low, name)


def getAllExternalObj():
    global external_objs
    objs = Utils.getCertainTypeWithCertainFunc(mset.getAllObjects, mset.ExternalObject)
    final_objs = []
    for obj in objs:
        if type(obj.parent) is not mset.BakerTargetObject:
            final_objs.append(obj)
    external_objs = final_objs
    return external_objs


def getSelectedExternalObj():
    global external_objs
    external_objs = Utils.getCertainTypeWithCertainFunc(mset.getSelectedObjects, mset.ExternalObject)
    return external_objs
