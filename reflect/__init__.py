# -*- coding: utf-8 -*-

__version__ = "0.0.0"

from .core import *
from .server import *

def setMode(mode):
  core.clips.mode = mode
