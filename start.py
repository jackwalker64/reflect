# -*- coding: utf-8 -*-

import argparse
import reflect
import os



def main():
  print("")

  reflect.setMode("server")

  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--debug", action = "store_true", help = "Enable debug mode.")
  parser.add_argument("-v", "--visualise", action = "store_true", help = "Write the priority graph to D:/Desktop/priorities.png every time it is updated.")
  parser.add_argument("-V", "--visualiseFilepath", required = False, default = None, help = "Write the priority graph to the specified path every time it is updated.")
  parser.add_argument("-t", "--disableTransformations", action = "store_true", help = "Prevent the order of effects from being automatically manipulated.")
  parser.add_argument("-f", "--filepath", required = False, default = None, help = "The path to the python script to watch.")
  parser.add_argument("-m", "--cacheSize", required = False, default = 100, help = "The maximum size, in MiB, of the cache. Default is 100 MiB.")
  parser.add_argument("-c", "--cacheAlgorithm", required = False, default = "specialised", choices = ["specialised", "fifo", "lru", "mru"], help = "The caching algorithm to use.")
  parser.add_argument("-s", "--enableStatistics", action = "store_true", help = "Collect information about cache hits and misses. Press `s` in the console to print the current statistics, or `r` to reset them.")
  parser.add_argument("-l", "--logFilepath", required = False, default = None, help = "Write the log output to the specified file.")
  args = parser.parse_args()

  defaultFilepath = "D:\\Documents\\University\\Year 3\\_Project\\Git\\reflect\\examples\\example.py"
  if args.debug:
    os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(761, 270)
    if args.filepath is None:
      filepath = defaultFilepath
    else:
      filepath = args.filepath
  else:
    filepath = args.filepath

  if args.visualiseFilepath is not None:
    reflect.setVisualiseFilepath(args.visualiseFilepath)
  elif args.visualise:
    reflect.setVisualiseFilepath("D:/Desktop/priorities.png")

  if args.disableTransformations:
    reflect.setTransformations([])
  else:
    reflect.setTransformations(["CanonicalOrder", "FlattenConcats"])

  reflect.server.debug = args.debug
  reflect.server.start(filepath, defaultFilepath, cacheSize = int(args.cacheSize) * 1024 * 1024, cacheAlgorithm = args.cacheAlgorithm, enableStatistics = args.enableStatistics, logFilepath = args.logFilepath)

  print("")



if __name__ == "__main__":
  main()
