# -*- coding: utf-8 -*-

import reflect
import os
import sys
import time
import logging


# limit = [1, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000][10]
limit = 1000
print("LIMIT = {}".format(limit))
logging.info("LIMIT = {}".format(limit))

directoryPath = "examples/2x2"
x = None
v = None
i = 0
sys.setrecursionlimit(30000)
for filename in os.listdir(directoryPath):
  filepath = os.path.join(directoryPath, filename)

  x = reflect.load(filepath)

  if v is None:
    v = x
  else:
    v = v.concat(x)

  i += 1
  if i >= limit:
    break
