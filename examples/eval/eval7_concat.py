# -*- coding: utf-8 -*-

import reflect
import os
import sys
import time


limits = [1000]
# limits = [2, 1000, 2000]

for limit in limits:
  t1 = time.perf_counter()

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

  t2 = time.perf_counter()
  print("LIMIT = {0}, T = {1:.16f} ms".format(limit, (t2 - t1) * 1000))
