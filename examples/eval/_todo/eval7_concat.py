# -*- coding: utf-8 -*-

import reflect
import os
import sys


directoryPath = "examples/2x2"
x = None
v = None
i = 0
limit = 2000
sys.setrecursionlimit(30000)
for filename in os.listdir(directoryPath):
  filepath = os.path.join(directoryPath, filename)

  if x is None:
    x = reflect.load(filepath)

  if v is None:
    v = x
  else:
    v = v.concat(x)

  i += 1
  if i >= limit:
    break

v = v.rate(fps = 100)
