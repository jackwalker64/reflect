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



def start(filepath, cacheSize):
  logging.basicConfig(format = "%(levelname)s: %(message)s", level = logging.NOTSET)

  logging.info("Starting the reflect server")
  logging.info("Watching {}".format(filepath))

  cache = reflect.Cache.current()
  cache.maxSize = cacheSize

  # Set up a handler to wait for the directory to be modified
  eventHandler = WatchdogHandler(filepath)
  observer = Observer()
  observer.schedule(eventHandler, path = os.path.dirname(filepath), recursive = False)
  observer.start()
  try:
    while True:
      key = reflect.util.getch()
      if key == b"\x03" or key == b"q":
        raise KeyboardInterrupt
      elif key == b" ":
        # Manually re-run the script
        runUserScript(filepath)
      else:
        try:
          char = key.decode("utf8")
          logging.error("Unrecognised command: {}".format(char))
        except UnicodeDecodeError as _:
          logging.error("Unrecognised command: {}".format(key))
  except KeyboardInterrupt:
    logging.info("Stopping")
    observer.stop()
  observer.join()



class WatchdogHandler(FileSystemEventHandler):
  def __init__(self, filepath):
    self.filepath = filepath
    self.filehash = None

  def on_modified(self, event):
    # Check that the modified file is actually the one we're watching
    if os.path.realpath(event.src_path) == os.path.realpath(self.filepath):
      # Check that the contents of the file really have changed
      with open(self.filepath, "rb") as f:
        newFilehash = hashlib.md5(f.read()).hexdigest()
      if newFilehash != self.filehash:
        self.filehash = newFilehash
        runUserScript(self.filepath)



def runUserScript(filepath):
  print("")
  print("")
  print("")
  print("")
  print("")
  logging.info("{}: Entering {}".format(datetime.datetime.now().isoformat(" "), os.path.basename(filepath)))
  print("")

  # Discard the old the composition graph
  reflect.CompositionGraph.reset()

  # Ensure any runtime render results are staged rather than immediately put into the main cache
  cache = reflect.Cache.current()
  cache.userScriptIsRunning = True

  # Construct the set of globals that will be passed to the user's script
  globs = { "__name__": "__main__" }

  # Execute the user's script
  with open(filepath) as f:
    try:
      exec(f.read(), globs)
    except Exception as e:
      traceback.print_exc()

  print("")
  logging.info("{}: Exited {}".format(datetime.datetime.now().isoformat(" "), os.path.basename(filepath)))

  print("")
  logging.info(cache)
  print("")
  cache.userScriptIsRunning = False

  # Update priorities according to the new composition graph
  cache.reprioritise(reflect.CompositionGraph.current())

  # TODO: Commit any staged frames into the main cache
  cache.commit()

  print("")
  logging.info(cache)

  # Close readers that were opened in the previous session but not claimed in the current session
  for filepath, readers in reflect.core.vfx.load.readyReaders.items():
    for reader in readers:
      reader.close()
  reflect.core.vfx.load.readyReaders = {}

  # Make readers opened in the current session available to the next session
  reflect.core.vfx.load.readyReaders = reflect.core.vfx.load.openReaders
  reflect.core.vfx.load.openReaders = {}
