# -*- coding: utf-8 -*-

import time
import pygame
import imageio
import logging
import queue
import cv2
import math



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
    self._timelinePanel = pygame.Rect(0, self._displayPanel.bottom, self._windowWidth, 8)
    self._controlbarPanel = pygame.Rect(0, self._timelinePanel.bottom, self._windowWidth, 25)

    self._windowHeight = self._tabstripPanel.height + self._timelinePanel.height + self._controlbarPanel.height + self._displayPanel.height

    pygame.display.init()
    pygame.display.set_caption("Reflect")
    self._screen = pygame.display.set_mode((self._windowWidth, self._windowHeight))
    self._screen.fill((0, 0, 0))
    self._screen.fill((39, 40, 34), rect = self._tabstripPanel)
    self._screen.fill((127, 127, 127), rect = self._displayPanel)
    self._screen.fill((174, 174, 174), rect = self._timelinePanel)
    self._screen.fill((39, 40, 34), rect = self._controlbarPanel)
    pygame.display.update()

    self._running = True

    self._leaves = None # List of leaf clips which can be previewed
    self._currentTab = None # Index of the currently visible leaf clip
    self._currentFrame = None

    self._playing = False
    self._currentFrame = 0

    self._heldKeys = {} # keycode → int. Keeps track of how many frames each key has been held for.
    self._heldMouseButtons = {} # buttoncode → dict. Keeps track of how many frames each mouse button has been held for, and the position of the click.



  def run(self):
    # Preview window event loop

    while self._running:
      # Handle any incoming method calls
      while not self._callQueue.empty():
        f, args, kwargs = self._callQueue.get(block = False)
        f(*args, **kwargs)
        self._callQueue.task_done()

      # Process gui input
      for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
          self._heldMouseButtons[event.button] = {
            "initialPosition": pygame.mouse.get_pos(),
            "duration": 0
          }
        elif event.type == pygame.MOUSEBUTTONUP:
          del self._heldMouseButtons[event.button] # Button is no longer being held
        elif event.type == pygame.KEYDOWN:
          self._heldKeys[event.key] = 0 # Key has been held for 0 frames
        elif event.type == pygame.KEYUP:
          del self._heldKeys[event.key] # Key is no longer being held
        elif event.type == pygame.QUIT:
          logging.info("Stopping")
          self._running = False
          break

      for button, state in self._heldMouseButtons.items():
        initialX, initialY = state["initialPosition"]
        duration = state["duration"]
        x, y = pygame.mouse.get_pos()
        if button == 1:
          # Left click
          if self._timelinePanel.collidepoint(initialX, initialY):
            # Seek to position
            targetFrame = math.floor(x / self._timelinePanel.width * self._leaves[self._currentTab].frameCount)
            if targetFrame >= self._leaves[self._currentTab].frameCount:
              targetFrame = self._leaves[self._currentTab].frameCount - 1
            elif targetFrame < 0:
              targetFrame = 0
            self._seek(n = targetFrame)
        elif button == 2:
          # Middle click
          if self._displayPanel.collidepoint(x, y):
            if duration == 0:
              # Pause/unpause
              self._playing = not self._playing
      for button in self._heldMouseButtons:
        self._heldMouseButtons[button]["duration"] += 1 # Button has been held for one more frame

      # Handle keys that were pressed/held
      for key, duration in self._heldKeys.items():
        if key == pygame.K_RIGHT:
          if duration == 0 or duration > self._fps / 2:
            # Go to the next frame
            self._playing = False
            self._seek(relative = 1)
        elif key == pygame.K_LEFT:
          if duration == 0 or duration > self._fps / 2:
            # Go to the previous frame
            self._playing = False
            self._seek(relative = -1)
      for key in self._heldKeys:
        self._heldKeys[key] += 1 # Key has been held for one more frame

      # If the video is currently playing, update the display
      if self._playing:
        self._seek(relative = 1) # Seek to the next frame

      self._clock.tick(self._fps)

    pygame.quit()



  def _seek(self, n = None, relative = None):
    if n is not None:
      if relative is not None:
        raise Exception("Expected exactly one argument but received two")
      self._currentFrame[self._currentTab] = n
    elif relative is not None:
      self._currentFrame[self._currentTab] += relative
      if self._currentFrame[self._currentTab] >= self._leaves[self._currentTab].frameCount:
        self._currentFrame[self._currentTab] -= self._leaves[self._currentTab].frameCount
      elif self._currentFrame[self._currentTab] < 0:
        self._currentFrame[self._currentTab] += self._leaves[self._currentTab].frameCount
    else:
      raise Exception("Expected exactly one argument but received zero")

    self._updateDisplay()



  def stop(self, *args, **kwargs):
    self._callQueue.put((self._stop, args, kwargs))

  def _stop(self):
    self._running = False



  def startSession(self, *args, **kwargs):
    self._callQueue.put((self._startSession, args, kwargs))

  def _startSession(self, leaves):
    # Set up the leaves/tabs
    self._leaves = list(leaves)
    self._currentTab = 0
    self._currentFrame = [0] * len(self._leaves) # For each leaf, start at the first frame

    # Blit the first frame of the first leaf
    self._updateDisplay()



  def _updateDisplay(self):
    leaf = self._leaves[self._currentTab]
    n = self._currentFrame[self._currentTab]

    image = leaf.frame(n)

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

    self._screen.fill((127, 127, 127), rect = self._displayPanel)

    surface = pygame.surfarray.make_surface(image.swapaxes(0, 1))
    self._screen.blit(surface, (blitRect.left, blitRect.top))

    pygame.display.update(self._displayPanel)

    # Update the timeline
    self._screen.fill((174, 174, 174), rect = self._timelinePanel)
    handleWidth = self._timelinePanel.height
    handleHeight = handleWidth
    handleLeft = n / (leaf.frameCount - 1) * (self._timelinePanel.width - handleWidth)
    handleRect = pygame.Rect(handleLeft, self._timelinePanel.top, handleWidth, handleHeight)
    self._screen.fill((255, 255, 255), rect = handleRect)
    pastRect = pygame.Rect(0, self._timelinePanel.top, handleRect.left, self._timelinePanel.height)
    self._screen.fill((241, 43, 36), rect = pastRect)
    pygame.display.update(self._timelinePanel)
