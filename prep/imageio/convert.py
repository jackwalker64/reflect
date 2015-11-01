import imageio
import time
import pygame

startTime = time.time()
print("Start time: {}".format(startTime))
print("")

reader = imageio.get_reader("../../examples/sources/bbb480.avi")
fps = reader.get_meta_data()["fps"]
print("FPS of bbb480.avi: {}".format(fps))

reader = imageio.get_reader("../../examples/sources/bbb1080.mp4")
fps = reader.get_meta_data()["fps"]
print("FPS of bbb1080.mp4: {}".format(fps))

# writer = imageio.get_writer("../../examples/dump/out1.mp4", fps=fps)
# for i in range(0, len(reader), 2000):
#   t1 = time.time()
#   im = reader.get_data(i)
#   t2 = time.time()
#   print("Frame {} took {} seconds to retrieve".format(i, t2 - t1))
#   writer.append_data(im)
#   t3 = time.time()
#   print("Frame {} took {} seconds to write".format(i, t3 - t2))
# t1 = time.time()
# writer.close()
# t2 = time.time()
# print("Writing took {} seconds".format(t2 - t1))
# print("")

writer = imageio.get_writer("../../examples/dump/out2.mp4", fps=30)
im = reader.get_data(4000)
writer.append_data(im)
for i in range(0, 90):
  # t1 = time.time()
  im = reader.get_next_data()
  # t2 = time.time()
  # print("Frame {} took {} seconds to retrieve".format(i, t2 - t1))
  writer.append_data(im)
  # t3 = time.time()
  # print("Frame {} took {} seconds to write".format(i, t3 - t2))
writer.close()
print("")

endTime = time.time()
print("End time: {}".format(endTime))
print("Total time: {}".format(endTime - startTime))
