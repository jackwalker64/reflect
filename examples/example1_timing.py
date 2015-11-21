# -*- coding: utf-8 -*-

import reflect
import imageio
import time

a = reflect.load("D:\\Documents\\University\\Year 3\\_Project\\Media\\sources\\bbb1080.mp4")

b = a.resize(height = 480)

t1 = time.time()
z = a.frame(5000)
print("Extracted source frame 5000 in {} seconds".format(time.time() - t1))
# imageio.imwrite("D:\\Documents\\University\\Year 3\\_Project\\Media\\dump\\source5000.png", a.frame(5000))

t1 = time.time()
z = b.frame(5000)
print("Extracted resized frame 5000 in {} seconds".format(time.time() - t1))
# imageio.imwrite("D:\\Documents\\University\\Year 3\\_Project\\Media\\dump\\resized5000.png", b.frame(5000))

t1 = time.time()
z = b.frame(7000)
print("Extracted resized frame 7000 in {} seconds".format(time.time() - t1))
# imageio.imwrite("D:\\Documents\\University\\Year 3\\_Project\\Media\\dump\\resized7000.png", b.frame(7000))

t1 = time.time()
z = a.frame(7000)
print("Extracted source frame 7000 in {} seconds".format(time.time() - t1))
# imageio.imwrite("D:\\Documents\\University\\Year 3\\_Project\\Media\\dump\\source7000.png", a.frame(7000))
