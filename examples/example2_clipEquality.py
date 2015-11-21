# -*- coding: utf-8 -*-

import reflect
import imageio
import time
import inspect

a = reflect.load("D:\\Documents\\University\\Year 3\\_Project\\Media\\sources\\bbb1080.mp4")
b = a.resize(size = 480/1080)
c = a.resize(size = 480/1080)
d = a.resize(height = 480)
e = a.resize(width = 853)

a2 = reflect.load("D:\\Documents\\University\\Year 3\\_Project\\Media\\sources\\bbb1080.mp4")
b2 = a2.resize(480/1080)

print("a.__hash__() == {}".format(a.__hash__()))
print("b.__hash__() == {}".format(b.__hash__()))
print("c.__hash__() == {}".format(c.__hash__()))
print("d.__hash__() == {}".format(d.__hash__()))
print("e.__hash__() == {}".format(e.__hash__()))
print("a2.__hash__() == {}".format(a2.__hash__()))
print("b2.__hash__() == {}".format(b2.__hash__()))

s = set([a, b, c, d, e, a2, b2])

print("")
print("[a, b, c, d, e, a2, b2]:")
for x in [a, b, c, d, e, a2, b2]:
  print(x)
print("")
print("set([a, b, c, d, e, a2, b2]):")
for x in s:
  print(x)
# print("len(set([a, b, c, d, e, a2, b2])) == {}".format(len(s)))
print("")
