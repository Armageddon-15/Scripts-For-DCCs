import os


def makeDir(path):
    if not os.path.exists(path):
        os.makedirs(path)