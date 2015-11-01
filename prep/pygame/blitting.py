import numpy
import imageio
import pygame
import cv2
import time

startTime = time.time()
print("Start time: {}".format(startTime))
print("")



reader = imageio.get_reader("../../examples/videos/bbb1080.mp4")
fps = reader.get_meta_data()["fps"]
print("FPS of bbb1080.mp4: {}".format(fps))

im0 = reader.get_data(4000)
im = cv2.resize(+im0.astype("uint8"), (853, 480), interpolation = cv2.INTER_AREA)
frames = []
frames.append(im)
frames.append(cv2.resize(+im0.astype("uint8"), (853, 480), interpolation = cv2.INTER_NEAREST))
frames.append(im[:, :, 2])
imT = im.copy()
imT[imT < 200] = 0
frames.append(imT)
imT = im.copy()
imT[imT < 200] += 50
imT -= 200
imT *= 4
frames.append(imT)
imT = im.copy()
imT[imT < 200] = 0
imT -= 200
imT *= 4
frames.append(imT)
currentFrame = 0

screen = pygame.display.set_mode((853, 480))
im = frames[currentFrame]
a = pygame.surfarray.make_surface(im.swapaxes(0, 1))
screen.blit(a, (0, 0))
pygame.display.flip()

running = True
while running:
  for event in pygame.event.get():
    if event.type == pygame.MOUSEBUTTONDOWN:
      x, y = pygame.mouse.get_pos()
      rgb = im[y, x]
      print("position, color: %s, %s" % (str((x, y)), str(rgb)))
      if currentFrame < len(frames) - 1:
        currentFrame += 1
      else:
        currentFrame = 0
      im = frames[currentFrame]
      a = pygame.surfarray.make_surface(im.swapaxes(0, 1))
      screen.blit(a, (0, 0))
      pygame.display.flip()
    elif event.type == pygame.QUIT:
      running = False
  time.sleep(1/fps)



endTime = time.time()
print("End time: {}".format(endTime))
print("Total time: {}".format(endTime - startTime))

