# -*- coding: utf-8 -*-

__version__ = "0.0.0"

from .core import *
from .server import *
from .core.vfx.load import load # Make the load function easily accessible as reflect.load

def setMode(mode):
  core.clips.mode = mode
