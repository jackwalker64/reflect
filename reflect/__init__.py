# -*- coding: utf-8 -*-

__version__ = "0.0.0"

from .core import *
from .server import *

# Make the root functions easily accessibly as reflect.<fn>
from .core.roots.load import load
from .core.roots.text import text

def setMode(mode):
  core.clips.mode = mode
