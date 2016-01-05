# -*- coding: utf-8 -*-

import time
import pygame
import imageio
import logging
import queue
import cv2



class Window(object):
  """Window()

  This class controls the preview window GUI.
  """



  def __init__(self):
    super().__init__()

    self._callQueue = queue.Queue()

    self._clock = pygame.time.Clock()
    self._fps = 20 # Defines the responsiveness of the GUI

    self._windowWidth = 900

    self._tabstripPanel = pygame.Rect(0, 0, self._windowWidth, 25)
    self._displayPanel = pygame.Rect(0, self._tabstripPanel.bottom, self._windowWidth, 480)
    self._timelinePanel = pygame.Rect(0, self._displayPanel.bottom, self._windowWidth, 13)
    self._controlbarPanel = pygame.Rect(0, self._timelinePanel.bottom, self._windowWidth, 25)

    self._windowHeight = self._tabstripPanel.height + self._timelinePanel.height + self._controlbarPanel.height + self._displayPanel.height

    pygame.display.init()
    pygame.display.set_caption("Reflect")
    self._screen = pygame.display.set_mode((self._windowWidth, self._windowHeight))
    self._screen.fill((0, 0, 0))
    self._screen.fill((39, 40, 34), rect = self._tabstripPanel)
    self._screen.fill((127, 127, 127), rect = self._displayPanel)
    self._screen.fill((39, 40, 34), rect = self._timelinePanel)
    self._screen.fill((39, 40, 34), rect = self._controlbarPanel)
    pygame.display.update()

    self._running = True



  def run(self):
    while self._running:
      # Handle any incoming method calls
      while not self._callQueue.empty():
        f, args, kwargs = self._callQueue.get(block = False)
        f(*args, **kwargs)
        self._callQueue.task_done()

      for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
          # TODO: Implement buttons
          pass
        elif event.type == pygame.QUIT:
          logging.info("Stopping")
          self._running = False
          break

      self._clock.tick(self._fps)

    pygame.quit()



  def stop(self, *args, **kwargs):
    self._callQueue.put((self._stop, args, kwargs))

  def _stop(self):
    self._running = False



  def startSession(self, *args, **kwargs):
    self._callQueue.put((self._startSession, args, kwargs))

  def _startSession(self, leaves):
    for leaf in leaves:
      break

    image = leaf.frame(0)

    if self._displayPanel.width >= leaf.width and self._displayPanel.height >= leaf.height:
      # The frame is smaller than the display panel, so put the frame in the centre
      blitRect = pygame.Rect(
        (self._displayPanel.width - leaf.width) / 2,
        self._displayPanel.top + (self._displayPanel.height - leaf.height) / 2,
        leaf.width,
        leaf.height
      )
    elif self._displayPanel.width / self._displayPanel.height >= leaf.width / leaf.height:
      # The display panel is wider than the frame to be blitted, so pillarbox the frame
      height = self._displayPanel.height
      width = leaf.width / leaf.height * height
      top = self._displayPanel.top
      left = (self._displayPanel.width - width) / 2
      blitRect = pygame.Rect(left, top, width, height)
      if leaf.height > blitRect.height:
        # Downscale the frame to match the display panel's height
        image = cv2.resize(image, (blitRect.width, blitRect.height), interpolation = cv2.INTER_AREA)
    else:
      # The display panel is taller than the frame to be blitted, so letterbox the frame
      width = self._displayPanel.width
      height = leaf.height / leaf.width * width
      left = self._displayPanel.left
      top = (self._displayPanel.height - height) / 2
      blitRect = pygame.Rect(left, top, width, height)
      if leaf.width > blitRect.width:
        # Downscale the frame to match the display panel's width
        image = cv2.resize(image, (blitRect.width, blitRect.width), interpolation = cv2.INTER_AREA)

    surface = pygame.surfarray.make_surface(image.swapaxes(0, 1))
    self._screen.blit(surface, (blitRect.left, blitRect.top))

    pygame.display.update(self._displayPanel)
