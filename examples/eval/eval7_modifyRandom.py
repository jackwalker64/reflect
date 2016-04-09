# -*- coding: utf-8 -*-

import reflect
import time
import random

# random.seed(42)





try:
  r = random.randint(0, 2*60+3-1)
  print("Adding to {}".format(r))
  reflect.server.BLUR_AMOUNT[r] += 1
  reflect.server.IT_COUNT += 1
except AttributeError:
  reflect.server.BLUR_AMOUNT = { i: 1 for i in range(123) }
  reflect.server.IT_COUNT = 1

print("IT_COUNT = {}".format(reflect.server.IT_COUNT))

def B(i):
  return reflect.server.BLUR_AMOUNT[i]



x = reflect.load("D:/Documents/University/Year 3/_Project/Media/sources/bbb_480p.avi")

i = 0

x = x.blur(B(i))
i += 1

for i in range(60):
  x = x.blur(B(i))
  i += 1

x = x.blur(B(i))
i += 1

for i in range(60):
  x = x.blur(B(i))
  i += 1

x = x.blur(B(i))
i += 1

x = x.subclip(1000, 1002) # the first frame will be requested for the tab thumbnail
