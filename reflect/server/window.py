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
    self._displayPanel = pygame.Rect(0, self._tabstripPanel.bottom, self._windowWidth, 540)
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

    self._leaves = [] # List of leaf dicts, each one containing a reference to the leaf clip as well as state like current frame and tab icon
    self._currentTab = None # Index of the currently visible leaf clip

    self._playing = False

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
      scrollWheel = 0
      for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
          if event.button == 4:
            scrollWheel += 1
          elif event.button == 5:
            scrollWheel -= 1
          else:
            self._heldMouseButtons[event.button] = {
              "initialPosition": pygame.mouse.get_pos(),
              "duration": 0
            }
        elif event.type == pygame.MOUSEBUTTONUP:
          if event.button in self._heldMouseButtons:
            del self._heldMouseButtons[event.button] # Button is no longer being held
        elif event.type == pygame.KEYDOWN:
          self._heldKeys[event.key] = 0 # Key has been held for 0 frames
        elif event.type == pygame.KEYUP:
          if event.key in self._heldKeys:
            del self._heldKeys[event.key] # Key is no longer being held
        elif event.type == pygame.MOUSEMOTION:
          # Check the position of the mouse
          (mouseX, mouseY) = pygame.mouse.get_pos()
          if self._tabstripPanel.collidepoint(mouseX, mouseY):
            self._redrawTabstrip()
        elif event.type == pygame.QUIT:
          logging.info("Stopping")
          self._running = False
          break

      if not self._leaves:
        # Check for a left click in the display area, which will trigger a script run
        for button, state in self._heldMouseButtons.items():
          initialX, initialY = state["initialPosition"]
          duration = state["duration"]
          if button == 1 and duration == 0 and self._displayPanel.collidepoint(initialX, initialY) and not self.userScriptIsRunning:
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
            if self._tabstripPanel.collidepoint(initialX, initialY):
              if duration == 0:
                self._clickTab(mousePosition = (initialX, initialY))
            elif self._timelinePanel.collidepoint(initialX, initialY):
              # Seek to position
              targetFrame = math.floor(x / self._timelinePanel.width * self._leaves[self._currentTab]["clip"].frameCount)
              if targetFrame >= self._leaves[self._currentTab]["clip"].frameCount:
                targetFrame = self._leaves[self._currentTab]["clip"].frameCount - 1
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
          elif button == 3:
            # Right click
            if self._displayPanel.collidepoint(x, y):
              if duration == 0:
                # Copy the current frame to the clipboard
                import win32clipboard
                import tempfile
                with tempfile.NamedTemporaryFile(suffix = ".bmp", delete = False) as t:
                  leaf = self._leaves[self._currentTab]["clip"]
                  image = leaf.frame(self._leaves[self._currentTab]["currentFrame"])
                  imageio.imwrite(t.name, image)
                  data = t.read()[14:]
                os.remove(t.name)
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
                logging.info("Copied frame to the clipboard")

        # Handle the scroll wheel
        if scrollWheel > 0:
          # Wheel scroll up
          x, y = pygame.mouse.get_pos()
          if self._tabstripPanel.collidepoint(x, y):
            self._clickTab(tabIndex = self._currentTab + 1 if self._currentTab + 1 < len(self._leaves) else 0)
        elif scrollWheel < 0:
          # Wheel scroll down
          x, y = pygame.mouse.get_pos()
          if self._tabstripPanel.collidepoint(x, y):
            self._clickTab(tabIndex = self._currentTab - 1 if self._currentTab - 1 >= 0 else len(self._leaves) - 1)

        # Handle keys that were pressed/held
        for key, duration in self._heldKeys.items():
          if key == pygame.K_RIGHT:
            if duration == 0 or duration > self._fps / 2:
              if pygame.K_LSHIFT in self._heldKeys or pygame.K_RSHIFT in self._heldKeys:
                # + 3 s
                self._redrawPlayButton()
                self._seek(relative = math.ceil(self._fps * 3), loop = False)
              elif pygame.K_LCTRL in self._heldKeys or pygame.K_RCTRL in self._heldKeys:
                # + 60 s
                self._redrawPlayButton()
                self._seek(relative = math.ceil(self._fps * 60), loop = False)
              else:
                # Go to the next frame
                self._playing = False
                self._redrawPlayButton()
                self._seek(relative = 1)
          elif key == pygame.K_LEFT:
            if duration == 0 or duration > self._fps / 2:
              if pygame.K_LSHIFT in self._heldKeys or pygame.K_RSHIFT in self._heldKeys:
                # - 3 s
                self._redrawPlayButton()
                self._seek(relative = -math.ceil(self._fps * 3), loop = False)
              elif pygame.K_LCTRL in self._heldKeys or pygame.K_RCTRL in self._heldKeys:
                # - 60 s
                self._redrawPlayButton()
                self._seek(relative = -math.ceil(self._fps * 60), loop = False)
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
          elif key == pygame.K_F5:
            if duration == 0:
              # Save a snapshot
              filepath = "{0}_{1:0>{width}}.png".format(
                os.path.splitext(self._filepath)[0],
                self._leaves[self._currentTab]["currentFrame"],
                width = math.floor(math.log10(self._leaves[self._currentTab]["clip"].frameCount)) + 1
              )
              if pygame.K_LCTRL in self._heldKeys or pygame.K_RCTRL in self._heldKeys:
                # If CTRL is held, then let the user choose where to save the snapshot
                import tkinter
                from tkinter import filedialog
                tkinter.Tk().withdraw() # Hide tkinter's root window
                response = filedialog.asksaveasfilename(
                  title = "Choose where to save the snapshot",
                  defaultextension = ".png",
                  filetypes = [("PNG image", "*.png")],
                  initialfile = filepath,
                )
                filepath = response
              if filepath:
                logging.info("Saving frame...")
                leaf = self._leaves[self._currentTab]["clip"]
                imageio.imwrite(filepath, leaf.frame(self._leaves[self._currentTab]["currentFrame"]))
                logging.info("Saved frame to {}".format(filepath))
          elif key == pygame.K_TAB:
            if duration == 0 or duration > self._fps / 2:
              if pygame.K_LCTRL in self._heldKeys or pygame.K_RCTRL in self._heldKeys:
                if pygame.K_LSHIFT in self._heldKeys or pygame.K_RSHIFT in self._heldKeys:
                  # Switch to the previous tab
                  self._clickTab(tabIndex = self._currentTab - 1 if self._currentTab - 1 >= 0 else len(self._leaves) - 1)
                else:
                  # Switch to the next tab
                  self._clickTab(tabIndex = self._currentTab + 1 if self._currentTab + 1 < len(self._leaves) else 0)

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
    def makeIcon(leaf):
      # Render the clip's frame and resize it to be used as an icon in the tabstrip
      image = leaf.frame(0)
      newHeight = self._tabstripPanel.height - 4
      newWidth = max(round(newHeight / 2), round(leaf.width * newHeight / leaf.height))
      resizedImage = cv2.resize(image, (newWidth, newHeight), interpolation = cv2.INTER_AREA)
      surface = pygame.surfarray.make_surface(resizedImage.swapaxes(0, 1))
      return surface

    def initialLeafPosition(oldLeaves, oldCurrentTab, leaf, i):
      if i < len(oldLeaves):
        oldFrame = oldLeaves[i]["currentFrame"]
        if oldFrame < leaf.frameCount:
          return oldFrame
        else:
          # The leaf has changed too much to allow us to retain the old video position, so just reset it to 0
          return 0
      else:
        return 0

    # Set up the leaves/tabs
    self._leaves = [{
      "clip": leaf,
      "currentFrame": initialLeafPosition(self._leaves, self._currentTab, leaf, i),
      "icon": makeIcon(leaf)
    } for i, leaf in enumerate(sorted(leaves, key = lambda leaf: leaf.timestamp))]

    if self._currentTab is None or self._currentTab >= len(self._leaves):
      # The old tab index is longer valid/possible, so just reset it to show the first tab
      self._currentTab = 0

    if failed:
      # The user's script produced an error
      self._showText("The script produced an error, see the console for details.")
    elif self._leaves:
      # Set up and blit the first frame of the first leaf
      (mouseX, mouseY) = pygame.mouse.get_pos()
      self._redrawTabstrip()
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
      return self._leaves[self._currentTab]["clip"].fps



  def _seek(self, n = None, relative = None, loop = True):
    if n is not None:
      if relative is not None:
        raise Exception("Expected exactly one of `n` or `relative`, but received both")
      self._leaves[self._currentTab]["currentFrame"] = n
    elif relative is not None:
      self._leaves[self._currentTab]["currentFrame"] += math.ceil(relative)
      frameCount = self._leaves[self._currentTab]["clip"].frameCount
      if loop:
        if frameCount == 0:
          raise Exception("Empty clip")
        while self._leaves[self._currentTab]["currentFrame"] >= frameCount:
          self._leaves[self._currentTab]["currentFrame"] -= frameCount
        while self._leaves[self._currentTab]["currentFrame"] < 0:
          self._leaves[self._currentTab]["currentFrame"] += frameCount
      else:
        if self._leaves[self._currentTab]["currentFrame"] >= frameCount:
          self._leaves[self._currentTab]["currentFrame"] = frameCount - 1
        elif self._leaves[self._currentTab]["currentFrame"] < 0:
          self._leaves[self._currentTab]["currentFrame"] = 0
    else:
      raise Exception("Expected exactly one of `n` or `relative`, but received neither")

    self._redrawDisplay()



  # If the leaf clip doesn't fit within the preview window,
  # then work out the size it should be resized to.
  def sizeToFitDisplayPanel(self, leaf):
    if self._displayPanel.width >= leaf.width and self._displayPanel.height >= leaf.height:
      # The frame is smaller than the display panel, so no resizing is necessary
      return (leaf.width, leaf.height)
    elif self._displayPanel.width / self._displayPanel.height >= leaf.width / leaf.height:
      # The display panel is wider than the frame to be blitted, so pillarbox the frame
      if leaf.height > self._displayPanel.height:
        # Downscale the frame to match the display panel's height
        return (leaf.width / leaf.height * self._displayPanel.height, self._displayPanel.height)
      else:
        return (leaf.width, leaf.height)
    else:
      # The display panel is taller than the frame to be blitted, so letterbox the frame
      if leaf.width > self._displayPanel.width:
        # Downscale the frame to match the display panel's width
        return (self._displayPanel.width, leaf.height / leaf.width * self._displayPanel.width)
      else:
        return (leaf.width, leaf.height)



  def _clickTab(self, mousePosition = None, tabIndex = None):
    if tabIndex is not None:
      self._currentTab = tabIndex
      self._redrawTabstrip()
      self._redrawDisplay()
      self._redrawPlayButton()
      return

    if mousePosition is None:
      raise TypeError("expected either tabIndex or mousePosition to be provided")
    (mouseX, mouseY) = mousePosition

    # Figure out which tab the user just clicked on
    (x, y) = (self._tabstripPanel.left, self._tabstripPanel.top)
    for i, leaf in enumerate(self._leaves):
      surface = leaf["icon"]
      iconRect = pygame.Rect(x + 2, y + 2, surface.get_width(), surface.get_height())
      if iconRect.collidepoint(mouseX, mouseY):
        self._currentTab = i
        self._redrawTabstrip()
        self._redrawDisplay()
        self._redrawPlayButton()
        return
      x += surface.get_width() + 2



  def _redrawTabstrip(self):
    self._screen.fill((39, 40, 34), rect = self._tabstripPanel)

    (x, y) = (self._tabstripPanel.left, self._tabstripPanel.top)
    (mouseX, mouseY) = pygame.mouse.get_pos()
    for i, leaf in enumerate(self._leaves):
      surface = leaf["icon"]
      iconRect = pygame.Rect(x + 2, y + 2, surface.get_width(), surface.get_height())
      surface.set_alpha(255 if i == self._currentTab or iconRect.collidepoint(mouseX, mouseY) else 120)
      self._screen.blit(surface, (x + 2, y + 2))
      x += surface.get_width() + 2

    pygame.display.update(self._tabstripPanel)



  # Triggered when the current frame changes.
  def _redrawDisplay(self):
    leaf = self._leaves[self._currentTab]["clip"]
    n = self._leaves[self._currentTab]["currentFrame"]

    image = leaf.frame(n)

    self._screen.fill((127, 127, 127), rect = self._displayPanel)

    # The leaf is assumed to fit within the display panel, so we just need to shift it
    # to be in the centre middle.
    (blitLeft, blitTop) = (self._displayPanel.left, self._displayPanel.top)
    blitLeft += (self._displayPanel.width - leaf.width) / 2
    blitTop += (self._displayPanel.height - leaf.height) / 2

    surface = pygame.surfarray.make_surface(image.swapaxes(0, 1))
    self._screen.blit(surface, (blitLeft, blitTop))

    pygame.display.update(self._displayPanel)

    self._redrawTimeline(n, leaf)
    self._redrawProgress(n, leaf)



  def _redrawTimeline(self, n, leaf):
    self._screen.fill((174, 174, 174), rect = self._timelinePanel)

    handleWidth = self._timelinePanel.height
    handleHeight = handleWidth
    if leaf.frameCount == 1:
      handleLeft = 0
    else:
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
      self._controlbarPanel.width - self._controlbarProgressTimecodeRect.left,
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

