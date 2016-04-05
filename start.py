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

  reflect.server.start(filepath, defaultFilepath, cacheSize = int(args.cacheSize) * 1024 * 1024, cacheAlgorithm = args.cacheAlgorithm)

  print("")



if __name__ == "__main__":
  main()
