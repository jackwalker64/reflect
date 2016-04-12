# -*- coding: utf-8 -*-

import reflect
import os
import sys
import logging
import time




directoryPath = "examples/eval/2x2"
x = None
v = None
i = 0
limit = [2, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200][10]
sys.setrecursionlimit(30000)

print("LIMIT = {}".format(limit))
logging.info("LIMIT = {}".format(limit))

filepaths = [os.path.join(directoryPath, filename) for filename in os.listdir(directoryPath)]
filepaths = filepaths[0:limit]
t1 = time.perf_counter()
roots = [reflect.load(filepath) for filepath in filepaths]
v = roots[0].concat(roots[1:])
t2 = time.perf_counter()
logging.info("Concatted (limit={}) in {} us".format(limit, round((t2 - t1) * 1000000, 5)))

t1 = time.perf_counter()
for i in range(limit):
  v = v.blur(1)
t2 = time.perf_counter()
logging.info("Pushed (limit={}) in {} us".format(limit, round((t2 - t1) * 1000000, 5)))
