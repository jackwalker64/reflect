# -*- coding: utf-8 -*-

# python start.py -d -f "D:\Documents\University\Year 3\_Project\Git\reflect\examples\example5_slideshow.py"

import reflect
import os

def letterbox(x, width, height):
  b = x.resize(height = height).gaussianBlur(31)
  b = b.crop(width = width, xc = b.width / 2)
  b = b.brighten(-0.5)
  x = x.resize(width = width)
  c = b.composite(x, x1 = 0, yc = b.height / 2)
  return c

def pillarbox(x, width, height):
  b = x.resize(width = width).gaussianBlur(31)
  b = b.crop(height = height, yc = b.height / 2)
  b = b.brighten(-0.5)
  x = x.resize(height = height)
  c = b.composite(x, y1 = 0, xc = b.width / 2)
  return c

directoryPath = "D:\\Documents\\University\\Year 3\\_Project\\Media\\sources\\images\\cambridge"
v = None
for filename in os.listdir(directoryPath):
  filepath = os.path.join(directoryPath, filename)

  x = reflect.load(filepath).speed(duration = 4)
  if x.width / x.height > 800/480:
    x = letterbox(x, 800, 480)
  else:
    x = pillarbox(x, 800, 480)

  if v is None:
    v = x
  else:
    v = v.slide(x, origin = "bottom", frameCount = 20, f = reflect.core.easing.inOutQuad)


