import sys
import os
import mset

file_path = mset.getPluginPath()
file_dir = os.path.dirname(file_path)
plugin_path_text_file = os.path.join(file_dir, "plugin_path.txt")
with open(plugin_path_text_file, "r") as f:
    plugin_path = f.read()
sys.path.append(plugin_path)


import MatchHiLowToBaker


MatchHiLowToBaker.main()