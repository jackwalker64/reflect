# -*- coding: utf-8 -*-

import reflect
import imageio
import time
import inspect

a = reflect.load("D:\\Documents\\University\\Year 3\\_Project\\Media\\sources\\bbb_1080p_30fps.mp4")
B = a.resize(1/16)
b = B.resize(width = 1920, height = 1080)

c = reflect.load("D:\\Documents\\University\\Year 3\\_Project\\Media\\sources\\bbb_1080p_30fps_copy.mp4")
d = c.crop(x1 = c.width / 2).subclip(n1 = 500, frameCount = 3000)

e = b.composite(d, x1 = b.width - d.width, t1 = 0)
f = e.resize(height = 240)

g = f.subclip(n1 = 1000, n2 = 1050)
h = f.subclip(t1 = 120, frameCount = 50)

i = g.concat(h)

try:
  reflect.Cache.scriptcounter += 1
except Exception as _:
  reflect.Cache.scriptcounter = 0

a._str = "a{}".format(reflect.Cache.scriptcounter)
B._str = "B{}".format(reflect.Cache.scriptcounter)
b._str = "b{}".format(reflect.Cache.scriptcounter)
c._str = "c{}".format(reflect.Cache.scriptcounter)
d._str = "d{}".format(reflect.Cache.scriptcounter)
e._str = "e{}".format(reflect.Cache.scriptcounter)
f._str = "f{}".format(reflect.Cache.scriptcounter)
g._str = "g{}".format(reflect.Cache.scriptcounter)
h._str = "h{}".format(reflect.Cache.scriptcounter)
i._str = "i{}".format(reflect.Cache.scriptcounter)

# _ = i.frame(0)
# _ = i.frame(1)

cache = reflect.Cache.current()
cache.userScriptIsRunning = False
cache.reprioritise(reflect.CompositionGraph.current())

t1 = time.time()
for x in range(25, 30):
  _ = i.frame(x)
t2 = time.time()
print(t2 - t1)

cache.visualisePriorities(reflect.CompositionGraph.current(), "D:\\Desktop\\priorities.png")


# t1 = time.time()
# for x in range(5):
#   _ = a.frame(1000 + x)
#   _ = a.frame(7000 + x)
# print(time.time() - t1)

# print(i.fps, i.frameCount, i.duration)

# print(f.fps, f.frameCount, f.duration)

# i.save("D:\\Documents\\University\\Year 3\\_Project\\Media\\dump\\i5.mp4", crf = 20)

# x = i.frame(1)

# print(reflect.Cache.current())
