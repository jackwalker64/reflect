# -*- coding: utf-8 -*-

import reflect
import time
import random

random.seed(42)





x = reflect.load("D:/Documents/University/Year 3/_Project/Media/sources/bbb_480p.avi")

for i in range(40):
  x = x.blur(1)

x = x.subclip(1000, 1200)
