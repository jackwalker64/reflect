# -*- coding: utf-8 -*-

import reflect
import os
import sys
import logging
import time


if "FlattenConcats" not in reflect.core.clips.transformations:
  reflect.core.clips.transformations.append("FlattenConcats")

# if "FlattenConcats" in reflect.core.clips.transformations and "CanonicalOrder" in reflect.core.clips.transformations:
#   reflect.core.clips.transformations = ["CanonicalOrder"]

directoryPath = "examples/2x2"
x = None
v = None
i = 0
limit = 1000
sys.setrecursionlimit(30000)

t1 = time.perf_counter()
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
logging.info("Concatted (limit={}) in {} us".format(limit, round((t2 - t1) * 1000000, 5)))


t1 = time.perf_counter()
v = v.resize((3000, 3000))
v = v.subclip(round(limit/10), v.frameCount - round(limit/10))
v = v.reverse()
v = v.rate(fps = 100)
v = v.greyscale()
v = v.brighten(-0.3)
v = v.resize((8, 8))
v = v.reverse()
t2 = time.perf_counter()
logging.info("Pushed (limit={}) in {} us".format(limit, round((t2 - t1) * 1000000, 5)))

