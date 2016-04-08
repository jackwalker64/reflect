# -*- coding: utf-8 -*-

import reflect
import time
import random

random.seed(42)





def V():
  try:
    reflect.server.BLUR_AMOUNT += 1
    b = reflect.server.BLUR_AMOUNT
  except AttributeError:
    reflect.server.BLUR_AMOUNT = 1
    b = reflect.server.BLUR_AMOUNT

  print("BLUR_AMOUNT = {}".format(b))

  return b


x = reflect.load("D:/Documents/University/Year 3/_Project/Media/sources/bbb_480p.avi")

x = x.blur(1)

for i in range(60):
  x = x.blur(1)

x = x.blur(1)

for i in range(60):
  x = x.blur(1)

x = x.blur(V())

x = x.subclip(1000, 1002) # the first frame will be requested for the tab thumbnail
