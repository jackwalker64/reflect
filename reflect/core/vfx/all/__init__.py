# -*- coding: utf-8 -*-

from ...clips import VideoClip

# Iterate through the files in the vfx directory, importing each function and binding it to the
# VideoClip class for convenience.
import os
vfxDirectoryPath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
for filename in os.listdir(vfxDirectoryPath):
  if filename.endswith(".py"):
    name = filename[:-3] # e.g. "resize" if filename == "resize.py"
    if name != "load": # load is a special function that shouldn't be used as a VideoClip method
      exec("from ..{} import {}".format(name, name)) # import the module
      exec("VideoClip.{} = {}".format(name, name)) # bind it to the VideoClip class
