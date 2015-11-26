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



def start(filepath):
  logging.basicConfig(format = "%(levelname)s: %(message)s", level = logging.NOTSET)

  logging.info("Starting the reflect server")
  logging.info("Watching {}".format(filepath))

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
        logging.error("Unrecognised command: {}".format(key.decode("utf8")))
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
  logging.info("{}: Entering {}".format(datetime.datetime.now().isoformat(" "), os.path.basename(filepath)))
  print("")

  # Reset the composition graph
  oldGraph = reflect.CompositionGraph.swap(reflect.CompositionGraph())

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

  newGraph = reflect.CompositionGraph.current()
  # TODO: Cache.usersScriptHasFinishedAndHereAreTheGraphsToCompare(oldGraph, newGraph)
