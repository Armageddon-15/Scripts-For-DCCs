import os


def getPluginCoreLocation():
    dir_name = os.path.dirname(__file__)
    dir_name = dir_name.replace("\\", "/")
    return dir_name


def getPluginLocation():
    dir_name = getPluginCoreLocation()
    dir_name = dir_name[:-5]
    return dir_name
