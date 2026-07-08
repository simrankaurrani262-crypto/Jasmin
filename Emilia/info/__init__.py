import os
from os.path import basename, dirname, isfile
from Emilia import LOGGER


def getListOfFiles(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if "__pycache__" not in fullPath:
            if os.path.isdir(fullPath):
                allFiles = allFiles + getListOfFiles(fullPath)
            else:
                allFiles.append(fullPath)

    return allFiles


tele_dir = os.path.join(dirname(dirname(__file__)), "tele")
mod_paths = getListOfFiles(dirName=dirname(__file__)) + getListOfFiles(
    dirName=tele_dir
)

all_modules = [
    f[:-3]
    for f in mod_paths
    if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
]

module_names = [
    basename(f)[:-3]
    for f in mod_paths
    if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
]

LOGGER.info("MODULES LOADED - " + ", ".join(module_names))
ALL_MODULES = sorted(all_modules)
__all__ = ALL_MODULES + ["ALL_MODULES"]
