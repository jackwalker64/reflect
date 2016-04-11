# -*- coding: utf-8 -*-

import numpy
from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, Plot, Figure, Package, Matrix
from pylatex.utils import italic
import os
import re
import math

if __name__ == "__main__":
  identifiers = ["eval7_concat_noopt", "eval7_concat_opt"]

  doc = Document()
  doc.packages.append(Package("geometry", options = ["tmargin=1cm", "lmargin=1cm"]))

  with doc.create(Section("Stuff")):
    coordinates = {}
    for identifier in identifiers:
      print("Preparing {}".format(identifier))
      coordinates[identifier] = []
      data = [[]] * 3
      for i in range(3):
        data[i] = [float("inf")] * 1000
        with open("../logs/{}_{}.log".format(identifier, i+1)) as f:
          j = 0
          for line in f:
            m = re.match(r"^INFO: Accessed frame (\d+) in (.+?) us$", line)
            if m is not None:
              a, b = m.groups()
              a = int(a)
              b = float(b) / 1000000
              assert(a == j)
              data[i][a] = b
              j += 1
      for i in range(len(data[0])):
        val = numpy.mean([data[k][i] for k in range(3)])
        coordinates[identifier].append((i, val*1000))

    options = "height=10cm, width=10cm, grid=major, ymin=(-1), ymax=(12), xlabel=frame, ylabel=access latency / ms"
    # options = "title={}, height=5cm, width=5cm, grid=major, xmin=({}), xmax=({}), ymin=({}), ymax=({})".format(algorithm, xmin, xmax, ymin, ymax)
    # if s["isLogScale"]:
    #   options = "ymode=log, " + options
      # , ytick={1,0.1,0.01,0.001, 0.0001, 0.00001, 0.000001}
    with doc.create(TikZ()):
      with doc.create(Axis(options = options)) as plot:
        for identifier in identifiers:
          color = {
            "eval7_concat_noopt": "red",
            "eval7_concat_opt": "blue"
          }[identifier]
          name = {
            "eval7_concat_noopt": "no optimisation",
            "eval7_concat_opt": "concat flattening"
          }[identifier]
          plot.append(Plot(name = name, options = "only marks,color={}".format(color), coordinates = coordinates[identifier]))

    name = "eval7_concat_runtime"
    print("Generating {}.pdf".format(name))
    doc.generate_pdf("../tex/{}".format(name), compiler = "D:/Software/texlive/bin/win32/pdflatex.exe")
    print("Generating {}.tex".format(name))
    doc.generate_tex("../tex/{}".format(name))
    print("Done {}.".format(name))
    print("")
























