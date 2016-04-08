# -*- coding: utf-8 -*-

import reflect
import os
import sys
import logging
import time



v = reflect.load("D:/Documents/University/Year 3/_Project/Media/sources/bbb_480p.avi")

v = v.resize(10)
v = v.reverse()
v = v.rate(fps = 100)
v = v.greyscale()
v = v.brighten(0.3)
v = v.resize(0.1)
v = v.crop(xc = v.width / 2, yc = v.height / 2, width = v.width / 2, height = v.height / 2)
v = v.reverse()


print(v.size)
