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



def start(filepath, alwaysRerunScripts = False):
  logging.basicConfig(format = "%(levelname)s: %(message)s", level = logging.NOTSET)

  logging.info("Starting the reflect server")
  logging.info("Watching {}".format(filepath))

  # Set up a handler to wait for the directory to be modified
  eventHandler = WatchdogHandler(filepath, alwaysRerunScripts)
  observer = Observer()
  observer.schedule(eventHandler, path = os.path.dirname(filepath), recursive = False)
  observer.start()
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    logging.info("Stopping")
    observer.stop()
  observer.join()



class WatchdogHandler(FileSystemEventHandler):
  def __init__(self, filepath, alwaysRerunScripts):
    self.filepath = filepath
    self.filehash = None
    self.alwaysRerunScripts = alwaysRerunScripts
    self.lastRunTime = 0

  def on_modified(self, event):
    # Check that the modified file is actually the one we're watching
    if os.path.realpath(event.src_path) == os.path.realpath(self.filepath):
      if self.alwaysRerunScripts:
        # Sometimes, multiple FileModifiedEvent will be received when the user saves their script.
        # To avoid running the script for each of these events, we need to debounce.
        currentTime = time.time()
        if currentTime - self.lastRunTime > 2:
          # The last run was more than 2 seconds ago, so we're ok to re-run it
          self.lastRunTime = currentTime
          runUserScript(self.filepath)
      else:
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

  # Construct the set of globals that will be passed to the user's script
  globs = {
    "__name__": "__main__",
    "__reflectMode__": "server"
  }

  # Execute the user's script
  with open(filepath) as f:
    try:
      exec(f.read(), globs)
    except Exception as e:
      traceback.print_exc()

  print("")
  logging.info("{}: Exited {}".format(datetime.datetime.now().isoformat(" "), os.path.basename(filepath)))
