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

debug = False



def start(filepath, defaultFilepath, cacheSize, cacheAlgorithm = None, enableStatistics = False, logFilepath = None):
  if logFilepath is not None:
    logging.basicConfig(format = "%(levelname)s: %(message)s", level = logging.NOTSET, filename = logFilepath)
  else:
    logging.basicConfig(format = "%(levelname)s: %(message)s", level = logging.NOTSET)

  logging.info("Starting the reflect server")

  if cacheAlgorithm is None:
    cacheKind = reflect.SpecialisedCache
  else:
    cacheKind = {
      "specialised": reflect.SpecialisedCache,
      "fifo": reflect.FIFOCache,
      "lru": reflect.LRUCache,
      "mru": reflect.MRUCache
    }[cacheAlgorithm]
  cache = cacheKind(cacheSize, enableStatistics = enableStatistics)
  reflect.Cache.current().swap(cache)
  logging.info("Using a {} cache with capacity {} MiB".format(type(cache).__name__, round(cache.maxSize / 1024 / 1024, 1)))

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
      self.checkAndUpdate()



  def on_moved(self, event):
    # Check that the modified file is actually the one we're watching
    if os.path.realpath(event.dest_path) == os.path.realpath(self._filepath):
      self.checkAndUpdate()



  def checkAndUpdate(self):
    if not self._previewWindow.userScriptIsRunning:
      # Check that the contents of the file really have changed
      with open(self._filepath, "rb") as f:
        newFilehash = hashlib.md5(f.read()).hexdigest()
      if newFilehash != self._filehash:
        self._filehash = newFilehash
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
        if isinstance(key, str):
          key = bytearray(key, "utf8")
        if key == b"\x03" or key == b"q":
          raise KeyboardInterrupt
        elif key == b"r":
          logging.info("Reset the cache statistics")
          reflect.Cache.current().resetStats()
        elif key == b"s":
          logging.info(reflect.Cache.current().stats())
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

    t1 = time.perf_counter()

    self._previewWindow.userScriptIsRunning = True
    self._previewWindow.startBusy()

    print("")
    print("")
    print("")
    print("")
    print("")
    logging.info("{}: Entering {}".format(datetime.datetime.now().isoformat(" "), os.path.basename(self._filepath)))

    # Discard the old the composition graph
    reflect.CompositionGraph.reset()

    # Ensure any runtime render results are staged rather than immediately put into the main cache
    cache = reflect.Cache.current()
    cache.userScriptIsRunning = True

    # Construct the set of globals that will be passed to the user's script
    globs = { "__name__": "__main__" }

    # Execute the user's script
    failed = False
    with open(self._filepath, encoding = "utf-8") as f:
      try:
        exec(f.read(), globs)
      except Exception:
        traceback.print_exc()
        failed = True

    logging.info("{}: Exited {}".format(datetime.datetime.now().isoformat(" "), os.path.basename(self._filepath)))

    print("")
    if debug:
      logging.info(cache)
    cache.userScriptIsRunning = False

    if failed:
      self._previewWindow.userScriptIsRunning = False
      self._previewWindow.stopBusy()
      self._previewWindow.startSession(set(), failed = True)
      cache.emptyStagingArea()
      return

    # Resize the output clips to match the size of the preview window
    leavesToResize = set(reflect.CompositionGraph.current().leaves)
    for leaf in leavesToResize:
      size = self._previewWindow.sizeToFitDisplayPanel(leaf)
      if size != leaf.size:
        finalLeaf = leaf.resize(size)
        finalLeaf._timestamp = leaf._timestamp

    # Flatten concats
    from ..core.clips import transformations
    if "FlattenConcats" in transformations:
      reflect.CompositionGraph.current().flattenConcats()


    # Update priorities according to the new composition graph
    cache.reprioritise(reflect.CompositionGraph.current())

    # Commit any staged frames into the main cache
    cache.commit()

    if debug:
      logging.info(cache)

    # Close readers that were opened in the previous session but not claimed in the current session
    for filepath, readers in reflect.core.roots.load.readyReaders.items():
      for reader in readers:
        reader.close()
    reflect.core.roots.load.readyReaders = {}

    # Make readers opened in the current session available to the next session
    reflect.core.roots.load.readyReaders = reflect.core.roots.load.openReaders
    reflect.core.roots.load.openReaders = {}

    # Start a preview session for this script
    self._previewWindow.userScriptIsRunning = False
    self._previewWindow.stopBusy()
    self._previewWindow.startSession(reflect.CompositionGraph.current().leaves)

    t2 = time.perf_counter()
    logging.info("Compilation took {0:.16f} s".format(t2 - t1))
    print("")
