# -*- coding: utf-8 -*-

import reflect
import os
import imageio
import time
import inspect
import random

random.seed(42)




x = reflect.load("D:/Documents/University/Year 3/_Project/Media/sources/bbb_1080p_30fps.mp4")

y = x.subclip(1619, duration = "2:30")
y = x.subclip(4819+6113)
y = x.subclip(4819+6113+2683)
