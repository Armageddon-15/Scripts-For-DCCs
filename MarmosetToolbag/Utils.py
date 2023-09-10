import os


def makeDir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def getCertainTypeWithCertainFunc(func, t):
    all_objects = func()
    certain_objects = []
    for obj in all_objects:
        if type(obj) is t:
            certain_objects.append(obj)

    return certain_objects