# -*- coding: utf-8 -*-

import reflect
import time

a = reflect.load("D:\\Documents\\University\\Year 3\\_Project\\Media\\sources\\bbb1080.mp4")
b = a.resize(size = 480/1080)
c = a.resize(size = 480/1080)
d = a.resize(height = 480)
e = a.resize(width = 853)

a2 = reflect.load("D:\\Documents\\University\\Year 3\\_Project\\Media\\sources\\bbb1080.mp4")
b2 = a2.resize(480/1080)

def extractFrame(v, n):
  t1 = time.time()
  _ = v.frame(n)
  t2 = time.time()
  print("{} / #{} / frame {} / {} seconds".format(id(v), v.__hash__(), n, t2 - t1))

extractFrame(a, 5000) # takes a while if not cached, because we need to jump to frame 5000
extractFrame(b, 5000) # takes a while on the first run, because cv2 hasn't warmed up yet
extractFrame(a2, 5000)
extractFrame(b2, 5000)

print("")

extractFrame(a, 7000) # takes a while if not cached, because we need to jump to frame 5000
extractFrame(b, 7000)
extractFrame(a2, 7000)
extractFrame(b2, 7000)

print("")

extractFrame(a, 7001)
extractFrame(b, 7001)
extractFrame(a2, 7001)
extractFrame(b2, 7001)

print("")

extractFrame(a, 5000)
extractFrame(b, 5000)
extractFrame(a2, 5000)
extractFrame(b2, 5000)
