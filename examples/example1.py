# -*- coding: utf-8 -*-

import reflect
import imageio

a = reflect.load("D:\\Documents\\University\\Year 3\\_Project\\Media\\sources\\bbb1080.mp4")
print(a.metadata)

b = a.resize(height = 480)
print(b.metadata)

print("Extracting source frame 5000")
imageio.imwrite("D:\\Documents\\University\\Year 3\\_Project\\Media\\dump\\source5000.png", a.frame(5000))

print("Extracting resized frame 5000")
imageio.imwrite("D:\\Documents\\University\\Year 3\\_Project\\Media\\dump\\resized5000.png", b.frame(5000))

print("Extracting resized frame 7000")
imageio.imwrite("D:\\Documents\\University\\Year 3\\_Project\\Media\\dump\\resized7000.png", b.frame(7000))

print("Extracting source frame 7000")
imageio.imwrite("D:\\Documents\\University\\Year 3\\_Project\\Media\\dump\\source7000.png", a.frame(7000))
