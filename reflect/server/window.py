# -*- coding: utf-8 -*-

import time
import pygame
import imageio
import logging



class Window(object):
  """Window()

  This class controls the preview window GUI.
  """



  def __init__(self, forceQuit):
    super().__init__()

    self._forceQuit = forceQuit

    self._clock = pygame.time.Clock()
    self._fps = 20 # Defines the responsiveness of the GUI

    self._tabstripHeight = 25
    self._timelineHeight = 13
    self._controlbarHeight = 25

    self._displayWidth = 853
    self._displayHeight = 480

    self._windowWidth = 900
    self._windowHeight = self._tabstripHeight + self._timelineHeight + self._controlbarHeight + self._displayHeight

    self._tabstripPanel = pygame.Rect(0, 0, self._windowWidth, 25)
    self._displayPanel = pygame.Rect(0, self._tabstripPanel.bottom, self._windowWidth, self._displayHeight)
    self._timelinePanel = pygame.Rect(0, self._displayPanel.bottom, self._windowWidth, self._timelineHeight)
    self._controlbarPanel = pygame.Rect(0, self._timelinePanel.bottom, self._windowWidth, self._controlbarHeight)

    pygame.display.init()
    pygame.display.set_caption("Reflect")
    self._screen = pygame.display.set_mode((self._windowWidth, self._windowHeight))
    self._screen.fill((0, 0, 0))
    self._screen.fill((39, 40, 34), rect = self._tabstripPanel)
    self._screen.fill((127, 127, 127), rect = self._displayPanel)
    self._screen.fill((39, 40, 34), rect = self._timelinePanel)
    self._screen.fill((39, 40, 34), rect = self._controlbarPanel)
    pygame.display.update()



  def run(self):
    while True:
      if not self._forceQuit.empty():
        # The console-handling thread has signified that the main program should terminate
        pygame.quit()
        return

      for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
          x, y = pygame.mouse.get_pos()
          print("mousedown at {}".format(str((x, y))))
        elif event.type == pygame.QUIT:
          logging.info("Stopping")
          pygame.quit()
          return

      self._clock.tick(self._fps)
