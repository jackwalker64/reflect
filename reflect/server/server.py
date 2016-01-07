# -*- coding: utf-8 -*-

import sys
import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import hashlib
import traceback
import datetime
import reflect
import queue
import threading
import tkinter
from tkinter import filedialog



def start(filepath, defaultFilepath, cacheSize):
  logging.basicConfig(format = "%(levelname)s: %(message)s", level = logging.NOTSET)

  logging.info("Starting the reflect server")

  if filepath is None:
    tkinter.Tk().withdraw() # Hide tkinter's root window
    response = filedialog.askopenfile(
      title = "Choose a script to preview",
      defaultextension = ".py",
      filetypes = [("Python script", "*.py")],
      initialfile = defaultFilepath,
    )
    if response is None:
      logging.info("Cancelled by user")
      return
    else:
      filepath = response.name

  logging.info("Watching {}".format(filepath))

  cache = reflect.Cache.current()
  cache.maxSize = cacheSize

  previewWindow = reflect.window.Window(filepath)

  # Set up a handler to wait for the directory to be modified
  eventHandler = WatchdogHandler(filepath, previewWindow)
  observer = Observer()
  observer.schedule(eventHandler, path = os.path.dirname(filepath), recursive = False)
  observer.start()

  # Set up a handler for any console input
  consoleHandler = ConsoleHandler(filepath, previewWindow)
  consoleHandler.daemon = True
  consoleHandler.start()

  # Start the main pygame loop
  previewWindow.run()

  observer.stop()
  observer.join()



class WatchdogHandler(FileSystemEventHandler):
  def __init__(self, filepath, previewWindow):
    self._filepath = filepath
    self._filehash = None
    self._previewWindow = previewWindow



  def on_modified(self, event):
    # Check that the modified file is actually the one we're watching
    if os.path.realpath(event.src_path) == os.path.realpath(self._filepath):
      # Check that the contents of the file really have changed
      with open(self._filepath, "rb") as f:
        newFilehash = hashlib.md5(f.read()).hexdigest()
      if newFilehash != self._filehash:
        self._filehash = newFilehash
        if not self._previewWindow.userScriptIsRunning:
          ScriptRunner(self._filepath, self._previewWindow).start()



class ConsoleHandler(threading.Thread):
  def __init__(self, filepath, previewWindow):
    super().__init__()

    self._filepath = filepath
    self._previewWindow = previewWindow



  def run(self):
    try:
      while True:
        key = reflect.util.getch()
        if key == b"\x03" or key == b"q":
          raise KeyboardInterrupt
        elif key == b" ":
          # Manually re-run the script
          if not self._previewWindow.userScriptIsRunning:
            ScriptRunner(self._filepath, self._previewWindow).start()
        else:
          try:
            char = key.decode("utf8")
            logging.error("Unrecognised command: {}".format(char))
          except UnicodeDecodeError as _:
            logging.error("Unrecognised command: {}".format(key))
    except KeyboardInterrupt:
      logging.info("Stopping")
      self._previewWindow.stop()



class ScriptRunner(threading.Thread):
  def __init__(self, filepath, previewWindow):
    super().__init__()

    self._filepath = filepath
    self._previewWindow = previewWindow



  def run(self):
    if self._previewWindow.userScriptIsRunning:
      raise Exception("Attempted to run the script while it is already running")

    self._previewWindow.userScriptIsRunning = True
    self._previewWindow.startBusy()

    print("")
    print("")
    print("")
    print("")
    print("")
    logging.info("{}: Entering {}".format(datetime.datetime.now().isoformat(" "), os.path.basename(self._filepath)))
    print("")

    # Discard the old the composition graph
    reflect.CompositionGraph.reset()

    # Ensure any runtime render results are staged rather than immediately put into the main cache
    cache = reflect.Cache.current()
    cache.userScriptIsRunning = True

    # Construct the set of globals that will be passed to the user's script
    globs = { "__name__": "__main__" }

    # Execute the user's script
    error = False
    with open(self._filepath, encoding = "utf-8") as f:
      try:
        exec(f.read(), globs)
      except Exception:
        traceback.print_exc()
        error = True

    print("")
    logging.info("{}: Exited {}".format(datetime.datetime.now().isoformat(" "), os.path.basename(self._filepath)))

    print("")
    logging.info(cache)
    print("")
    cache.userScriptIsRunning = False

    if error:
      cache.emptyStagingArea()
      return

    # Update priorities according to the new composition graph
    cache.reprioritise(reflect.CompositionGraph.current())

    # Commit any staged frames into the main cache
    cache.commit()

    print("")
    logging.info(cache)

    # Close readers that were opened in the previous session but not claimed in the current session
    for self._filepath, readers in reflect.core.vfx.load.readyReaders.items():
      for reader in readers:
        reader.close()
    reflect.core.vfx.load.readyReaders = {}

    # Make readers opened in the current session available to the next session
    reflect.core.vfx.load.readyReaders = reflect.core.vfx.load.openReaders
    reflect.core.vfx.load.openReaders = {}

    # Start a preview session for this script
    self._previewWindow.userScriptIsRunning = False
    self._previewWindow.stopBusy()
    self._previewWindow.startSession(reflect.CompositionGraph.current().leaves)
