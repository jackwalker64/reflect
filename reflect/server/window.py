# -*- coding: utf-8 -*-

import os
import time
import pygame
import imageio
import logging
import queue
import cv2
import math
from reflect.server import ScriptRunner
from reflect.core.util import frameToTimecode



class Window(object):
  """Window()

  This class controls the preview window GUI.
  """



  def __init__(self, filepath):
    super().__init__()

    self._filepath = filepath

    self._callQueue = queue.Queue()

    self._clock = pygame.time.Clock()

    # Load resources
    self._resources = {}
    busyFrames = pygame.image.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../resources/busy.png"))
    self._resources["busy"] = [busyFrames.subsurface(pygame.Rect(i * 16, 0, 16, 16)) for i in range(0, math.floor(busyFrames.get_width() / 16))]
    playFrames = pygame.image.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../resources/play.png"))
    self._resources["play"] = [playFrames.subsurface(pygame.Rect(i * 25, 0, 25, 25)) for i in range(0, 2)]

    # Set up the geometry of the window panels
    self._windowWidth = 900
    self._tabstripPanel = pygame.Rect(0, 0, self._windowWidth, 25)
    self._displayPanel = pygame.Rect(0, self._tabstripPanel.bottom, self._windowWidth, 480)
    self._timelinePanel = pygame.Rect(0, self._displayPanel.bottom, self._windowWidth, 8)
    self._controlbarPanel = pygame.Rect(0, self._timelinePanel.bottom, self._windowWidth, 25)
    self._controlbarPlayRect = pygame.Rect(self._controlbarPanel.left, self._controlbarPanel.top, 26, 25)
    self._controlbarProgressTimecodeRect = None
    self._controlbarProgressFrameRect = None
    self._windowHeight = self._tabstripPanel.height + self._timelinePanel.height + self._controlbarPanel.height + self._displayPanel.height

    # Show the initial panels
    pygame.init()
    pygame.display.init()
    pygame.display.set_caption("Reflect")
    self._screen = pygame.display.set_mode((self._windowWidth, self._windowHeight))
    self._screen.fill((0, 0, 0))
    self._screen.fill((39, 40, 34), rect = self._tabstripPanel)
    self._screen.fill((127, 127, 127), rect = self._displayPanel)
    self._screen.fill((174, 174, 174), rect = self._timelinePanel)
    self._screen.fill((39, 40, 34), rect = self._controlbarPanel)
    self._showText("To see the first preview, either save your script or click anywhere.")
    pygame.display.update()

    self._running = True # Is the preview window currently active?
    self.userScriptIsRunning = False # Is the user's script currently being executed?

    self._busy = None

    self._leaves = [] # List of leaf clips which can be previewed
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

      if not self._leaves:
        # Check for a left click in the display area, which will trigger a script run
        for button, state in self._heldMouseButtons.items():
          initialX, initialY = state["initialPosition"]
          duration = state["duration"]
          if button == 1 and duration == 0 and self._displayPanel.collidepoint(initialX, initialY):
            self._showText("")
            ScriptRunner(self._filepath, self).start()
      else:
        # Handle mouse buttons that were clicked/held
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
            elif self._controlbarPlayRect.collidepoint(initialX, initialY):
              if duration == 0:
                # Pause/unpause
                self._playing = not self._playing
                self._redrawPlayButton()
          elif button == 2:
            # Middle click
            if self._displayPanel.collidepoint(x, y):
              if duration == 0:
                # Pause/unpause
                self._playing = not self._playing
                self._redrawPlayButton()

        # Handle keys that were pressed/held
        for key, duration in self._heldKeys.items():
          if key == pygame.K_RIGHT:
            if duration == 0 or duration > self._fps / 2:
              if pygame.K_LSHIFT in self._heldKeys or pygame.K_RSHIFT in self._heldKeys:
                # + 5 s
                self._redrawPlayButton()
                self._seek(relative = self._fps * 5, loop = False)
              elif pygame.K_LCTRL in self._heldKeys or pygame.K_RCTRL in self._heldKeys:
                # + 60 s
                self._redrawPlayButton()
                self._seek(relative = self._fps * 60, loop = False)
              else:
                # Go to the next frame
                self._playing = False
                self._redrawPlayButton()
                self._seek(relative = 1)
          elif key == pygame.K_LEFT:
            if duration == 0 or duration > self._fps / 2:
              if pygame.K_LSHIFT in self._heldKeys or pygame.K_RSHIFT in self._heldKeys:
                # - 5 s
                self._redrawPlayButton()
                self._seek(relative = -self._fps * 5, loop = False)
              elif pygame.K_LCTRL in self._heldKeys or pygame.K_RCTRL in self._heldKeys:
                # - 60 s
                self._redrawPlayButton()
                self._seek(relative = -self._fps * 60, loop = False)
              else:
                # Go to the previous frame
                self._playing = False
                self._redrawPlayButton()
                self._seek(relative = -1)
          elif key == pygame.K_SPACE:
            if duration == 0:
              # Pause/unpause
              self._playing = not self._playing
              self._redrawPlayButton()

        # If the video is currently playing, update the display
        if self._playing:
          self._seek(relative = 1) # Seek to the next frame

      if self._busy is not None:
        # Show the `self._busy`th busy indicator
        busyRect = pygame.Rect(self._controlbarPanel.right - 25, self._controlbarPanel.top, 25, 25)
        self._screen.fill((39, 40, 34), rect = busyRect)
        self._screen.blit(self._resources["busy"][self._busy], (busyRect.left + 4, busyRect.top + 4))
        pygame.display.update(busyRect)
        if self._busy < len(self._resources["busy"]) - 1:
          self._busy += 1
        else:
          self._busy = 0

      # Update any keys or buttons that have been held for one more frame
      for button in self._heldMouseButtons:
        self._heldMouseButtons[button]["duration"] += 1
      for key in self._heldKeys:
        self._heldKeys[key] += 1

      # Show the current fps in the window caption
      reportedFps = self._clock.get_fps()
      if reportedFps > self._fps:
        # pygame.time.Clock should ensure this never happens, but it does anyway
        reportedFps = self._fps
      elif reportedFps >= 0.95 * self._fps:
        # The fps is within 5% of the target. Avoid dancing around a near-perfect number by just reporting it as perfect.
        reportedFps = self._fps
      pygame.display.set_caption("Reflect ({:.2f} / {:.2f})".format(reportedFps, self._fps))

      self._clock.tick(self._fps)

    pygame.quit()



  def stop(self, *args, **kwargs):
    self._callQueue.put((self._stop, args, kwargs))

  def _stop(self):
    self._running = False



  def startBusy(self, *args, **kwargs):
    self._callQueue.put((self._startBusy, args, kwargs))

  def _startBusy(self):
    self._busy = 0 # Number of frames we have been busy for



  def stopBusy(self, *args, **kwargs):
    self._callQueue.put((self._stopBusy, args, kwargs))

  def _stopBusy(self):
    self._busy = None

    busyRect = pygame.Rect(self._controlbarPanel.right - 25, self._controlbarPanel.top, 25, 25)
    self._screen.fill((39, 40, 34), rect = busyRect)
    pygame.display.update(busyRect)



  def startSession(self, *args, **kwargs):
    self._callQueue.put((self._startSession, args, kwargs))

  def _startSession(self, leaves, failed = False):
    # Set up the leaves/tabs
    self._leaves = list(leaves)
    self._currentTab = 0
    self._currentFrame = [0] * len(self._leaves) # For each leaf, start at the first frame

    if failed:
      # The user's script produced an error
      self._showText("The script produced an error, see the console for details.")
    elif self._leaves:
      # Blit the first frame of the first leaf
      self._redrawDisplay()
      self._redrawPlayButton()
    else:
      # The script hasn't produced any output
      self._showText("The script didn't produce any previewable clips.")



  def _showText(self, text):
    font = pygame.font.SysFont("sans", 25)
    text = font.render(text, True, (0, 0, 0))
    self._screen.fill((127, 127, 127), rect = self._displayPanel)
    self._screen.blit(text, (self._displayPanel.centerx - text.get_width() / 2, self._displayPanel.centery - text.get_height() / 2))
    pygame.display.update(self._displayPanel)



  @property
  def _fps(self):
    if not self._leaves:
      return 30
    else:
      return self._leaves[self._currentTab].fps



  def _seek(self, n = None, relative = None, loop = True):
    if n is not None:
      if relative is not None:
        raise Exception("Expected exactly one of `n` or `relative`, but received both")
      self._currentFrame[self._currentTab] = n
    elif relative is not None:
      self._currentFrame[self._currentTab] += math.ceil(relative)
      frameCount = self._leaves[self._currentTab].frameCount
      if loop:
        if frameCount == 0:
          raise Exception("Empty clip")
        while self._currentFrame[self._currentTab] >= frameCount:
          self._currentFrame[self._currentTab] -= frameCount
        while self._currentFrame[self._currentTab] < 0:
          self._currentFrame[self._currentTab] += frameCount
      else:
        if self._currentFrame[self._currentTab] >= frameCount:
          self._currentFrame[self._currentTab] = frameCount - 1
        elif self._currentFrame[self._currentTab] < 0:
          self._currentFrame[self._currentTab] = 0
    else:
      raise Exception("Expected exactly one of `n` or `relative`, but received neither")

    self._redrawDisplay()



  # Triggered when the current frame changes.
  def _redrawDisplay(self):
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

    self._redrawTimeline(n, leaf)
    self._redrawProgress(n, leaf)



  def _redrawTimeline(self, n, leaf):
    self._screen.fill((174, 174, 174), rect = self._timelinePanel)

    handleWidth = self._timelinePanel.height
    handleHeight = handleWidth
    handleLeft = n / (leaf.frameCount - 1) * (self._timelinePanel.width - handleWidth)
    handleRect = pygame.Rect(handleLeft, self._timelinePanel.top, handleWidth, handleHeight)
    self._screen.fill((255, 255, 255), rect = handleRect)

    pastRect = pygame.Rect(0, self._timelinePanel.top, handleRect.left, self._timelinePanel.height)
    self._screen.fill((241, 43, 36), rect = pastRect)

    pygame.display.update(self._timelinePanel)



  def _redrawPlayButton(self):
    rect = self._controlbarPlayRect

    self._screen.fill((39, 40, 34), rect = rect)
    pygame.draw.line(self._screen, (57, 58, 54), (rect.right - 1, rect.top), (rect.right - 1, rect.bottom))

    self._screen.blit(self._resources["play"][1 if self._playing else 0], (self._controlbarPanel.left, self._controlbarPanel.top))

    pygame.display.update(rect)



  def _redrawProgress(self, n, leaf):
    font = pygame.font.SysFont("Consolas", 12)
    text1 = font.render("{} / {}".format(frameToTimecode(n, leaf.fps), frameToTimecode(leaf.frameCount, leaf.fps)), True, (255, 255, 255))
    numberLength = math.floor(math.log10(leaf.frameCount)) + 1
    text2 = font.render("{0: >{width}} / {1}".format(n, leaf.frameCount, width = numberLength), True, (255, 255, 255))

    self._controlbarProgressTimecodeRect = pygame.Rect(
      self._controlbarPanel.left + 26,
      self._controlbarPanel.top,
      text1.get_width() + 20,
      25
    )
    self._controlbarProgressFrameRect = pygame.Rect(
      self._controlbarProgressTimecodeRect.right,
      self._controlbarPanel.top,
      text2.get_width() + 20,
      25
    )
    progressRect = pygame.Rect(
      self._controlbarProgressTimecodeRect.left,
      self._controlbarPanel.top,
      self._controlbarProgressTimecodeRect.width + self._controlbarProgressFrameRect.width,
      25
    )

    self._screen.fill((39, 40, 34), rect = progressRect)

    x = self._controlbarProgressTimecodeRect.left
    y = self._controlbarProgressTimecodeRect.top
    self._screen.blit(text1, (x + 9, y + 7))
    x = self._controlbarProgressTimecodeRect.right - 1
    pygame.draw.line(self._screen, (57, 58, 54), (x, y), (x, y + 25))

    x = self._controlbarProgressFrameRect.left
    y = self._controlbarProgressFrameRect.top
    self._screen.blit(text2, (x + 9, y + 7))
    x = self._controlbarProgressFrameRect.right - 1
    pygame.draw.line(self._screen, (57, 58, 54), (x, y), (x, y + 25))

    pygame.display.update(progressRect)

