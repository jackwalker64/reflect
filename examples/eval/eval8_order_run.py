# -*- coding: utf-8 -*-

import reflect
import os
import sys
import logging
import time




SIZE = [1, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000][20]
print("SIZE = {}".format(SIZE))
logging.info("SIZE = {}".format(SIZE))

x = reflect.load("D:/Documents/University/Year 3/_Project/Media/sources/bbb_480p.avi")

t1 = time.perf_counter()
x = x.resize((SIZE, SIZE))
x = x.greyscale()
x = x.brighten(-0.3)
t2 = time.perf_counter()
logging.info("Pushed in {} us".format(round((t2 - t1) * 1000000, 5)))

