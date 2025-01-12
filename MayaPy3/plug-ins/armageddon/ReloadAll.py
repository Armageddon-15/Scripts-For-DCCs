import importlib
import fnmatch
import os


def listFilesWithCertainExtension(path, file_extension):
    """ Recursively searches through the path and uses a
    generator to yield files with the provided file extension.

    Args:
        path (str): File path to search through.
        file_extension (str):  File extension needs to include the dot: '.py' as an example.

    Yields:
        str: The path of the file with the matching file extension.
    """
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*{}'.format(file_extension)):
            yield os.path.join(root, filename)


def reloadAllPythonFiles(exclude_filenames=None):
    """ Reloads all the Python files found in the maya_scripts_path variable.
    Has an exclude_packages variable to exclude packages that don't need to be reloaded.

    Returns:
        None
    """
    maya_scripts_path = os.path.dirname(__file__)
    maya_scripts_path = maya_scripts_path.replace("\\", "/")
    # print(maya_scripts_path)

    python_files = listFilesWithCertainExtension(maya_scripts_path, '.py')
    python_files = [py_file.replace('\\', '/') for py_file in python_files]
    
    # print("\n")
    # print(python_files)
    
    need_to_exclude = True
    
    if type(exclude_filenames) is str:
        exclude_packages = exclude_filenames

    elif type(exclude_filenames) is list:
        exclude_packages = [exclude_filenames]
    
    else:
        need_to_exclude = False 

    if need_to_exclude:
        exclude_paths = [os.path.join(maya_scripts_path, package) for package in exclude_packages]
        exclude_paths = [path.replace('\\', '/') for path in exclude_paths]
        
    package_name = maya_scripts_path.split("/")[-1]
    # print(package_name)
    
    # package_path = maya_scripts_path.split("/" + package_name)[0]
    # print(package_path)

    for py_file in python_files:
        
        if '__init__.py' in py_file or "ReloadAll.py" in py_file:
            continue
        
        if need_to_exclude:
            if any(x in py_file for x in exclude_paths):
                continue
            
            
        # print(maya_scripts_path + "/")

        module_name = py_file.split(maya_scripts_path + "/")[1]
        module_name = module_name.replace("/", ".")
        module_name = module_name.split(".py")[0]
        
        # print(module_name)

        # if 'Scripts' in package:
            # continue

        # script = py_file.split('/')[-1].split('.')[0]
        # # package_full_path = package

        module_full_name = '{}.{}'.format(package_name, module_name)
        print(module_full_name)

        module = importlib.import_module(module_full_name, package=None)
        print(str(module) + " is imp")
        importlib.reload(module)
        print("Reloaded '{}'".format(py_file))