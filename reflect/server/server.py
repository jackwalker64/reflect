# -*- coding: utf-8 -*-

import sys
import os
import time
import argparse
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import hashlib



def main():
  logging.basicConfig(format = "%(levelname)s: %(message)s", level = logging.NOTSET)

  parser = argparse.ArgumentParser()
  parser.add_argument("-f", "--filepath", required = False, default = "D:\\Documents\\University\\Year 3\\_Project\\Git\\reflect\\examples\\example1.py")
  args = parser.parse_args()

  logging.info("Starting the reflect server")
  logging.info("Watching {}".format(args.filepath))

  # Set up a handler to wait for the directory to be modified
  eventHandler = WatchdogHandler(args.filepath)
  observer = Observer()
  observer.schedule(eventHandler, path = os.path.dirname(args.filepath), recursive = False)
  observer.start()
  try:
    while True:
      time.sleep(1)
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
  logging.info("Executing {}".format(filepath))

  # Construct the set of globals that will be passed to the user's script
  globs = { "__name__": "__main__" }

  # Execute the user's script
  with open(filepath) as f:
    exec(f.read(), globs)



if __name__ == "__main__":
  print("")
  main()
  print("")
