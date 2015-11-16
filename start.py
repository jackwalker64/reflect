# -*- coding: utf-8 -*-

import argparse
import reflect



def main():
  print("")

  reflect.setMode("server")

  parser = argparse.ArgumentParser()
  parser.add_argument("-f", "--filepath", required = False, default = "D:\\Documents\\University\\Year 3\\_Project\\Git\\reflect\\examples\\example.py", help = "The path to the python script to watch.")
  parser.add_argument("-a", "--alwaysRerunScripts", action = "store_true", default = False, help = "Re-execute scripts whenever they are saved, regardless of whether or not their contents have changed.")
  args = parser.parse_args()

  reflect.server.start(args.filepath, alwaysRerunScripts = args.alwaysRerunScripts)

  print("")



if __name__ == "__main__":
  main()
