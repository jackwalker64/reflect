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
      data = []
      with open("../logs/{}_comp.log".format(identifier)) as f:
        for line in f:
          m = re.match(r"^INFO: Compilation took (.+?) s$", line)
          if m is not None:
            (a,) = m.groups()
            a = float(a)
            data.append(a)
      # data = data[0:24]
      limits = [1, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000]
      for i in range(int(len(data) / 4)):
        x = limits[i]
        y = numpy.mean([data[i*4+j] for j in range(1, 4)])
        coordinates[identifier].append((x, y))

    options = "height=10cm, width=10cm, grid=major, ymin=(-0.15), ymax=(2.7), xlabel=number of concatenated clips, ylabel=total compile time / s"
    # options = "height=10cm, width=10cm, grid=major, ymin=(-0.05), ymax=(0.7), xlabel=number of concatenated clips, ylabel=compile time / s"
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
          plot.append(Plot(name = name, options = "very thick,color={}".format(color), coordinates = coordinates[identifier]))

    name = "eval7_concat_compiletime"
    print("Generating {}.pdf".format(name))
    doc.generate_pdf("../tex/{}".format(name), compiler = "D:/Software/texlive/bin/win32/pdflatex.exe")
    print("Generating {}.tex".format(name))
    doc.generate_tex("../tex/{}".format(name))
    print("Done {}.".format(name))
    print("")



  # for identifier in identifiers:
  #   print("Preparing {}".format(identifier))

  #   doc = Document()
  #   doc.packages.append(Package("geometry", options = ["tmargin=1cm", "lmargin=1cm"]))

  #   for s in series:
  #     with doc.create(Section("Series: {}".format(s["name"]))):
  #       algorithms = ["fifo", "lru", "mru", "specialised"]
  #       # algorithms = ["mru", "specialised", "specialisedOrig"]
  #       data = { a: [] for a in algorithms }

  #       for algorithm in algorithms:
  #         with open("../logs/{}_{}.log".format(identifier, algorithm)) as f:
  #           t = 0
  #           for line in f:
  #             m = re.match(r"^INFO: Cache stats: (\d+) h / (\d+) ncm / (\d+) cm .*? hr$", line)
  #             if m is not None:
  #               h, ncm, cm = m.groups()
  #               h, ncm, cm = int(h), int(ncm), int(cm)
  #               data[algorithm].append((h, ncm, cm))
  #               t += 1
  #         xmax = len(data[algorithm])

  #       xmin = -0.1 * xmax
  #       xmax *= 1.1


  #       if identifier in s["yminmax"]:
  #         ymin, ymax = s["yminmax"][identifier]
  #       else:
  #         ymin = min([min([s["function"](h, ncm, cm) for (h, ncm, cm) in data[algorithm] if s["function"](h, ncm, cm) is not None] + [float("inf")]) for algorithm in algorithms])
  #         ymax = max([max([s["function"](h, ncm, cm) for (h, ncm, cm) in data[algorithm] if s["function"](h, ncm, cm) is not None] + [float("-inf")]) for algorithm in algorithms])

  #         if ymin == float("inf"):
  #           ymin = 0
  #         if ymax == float("-inf"):
  #           ymax = 0

  #         if s["isLogScale"]:
  #           ymax, ymin = math.log10(ymax), math.log10(ymin)
  #         ygap = (ymax - ymin) / 10
  #         ymax += ygap
  #         ymin -= ygap
  #         if s["isLogScale"]:
  #           ymax, ymin = pow(10, ymax), pow(10, ymin)
  #         ymin, ymax = round(ymin, 6), round(ymax, 6)

  #       for algorithm in algorithms:
  #         currentData = data[algorithm]

  #         options = "title={}, height=5cm, width=5cm, grid=major, xmin=({}), xmax=({}), ymin=({}), ymax=({})".format(algorithm, xmin, xmax, ymin, ymax)
  #         if s["isLogScale"]:
  #           options = "ymode=log, " + options
  #           # , ytick={1,0.1,0.01,0.001, 0.0001, 0.00001, 0.000001}
  #         with doc.create(TikZ()):
  #           with doc.create(Axis(options = options)) as plot:
  #             color = s["color"]
  #             f = s["function"]

  #             coordinates = []
  #             for (t, (h, ncm, cm)) in enumerate(currentData):
  #               y = f(h, ncm, cm)
  #               if y is not None:
  #                 coordinates.append((t, y))

  #             plot.append(Plot(options = "very thick,color={}".format(color), coordinates = coordinates))

  #   print("Generating {}.pdf".format(identifier))
  #   doc.generate_pdf("../tex/{}".format(identifier), compiler = "D:/Software/texlive/bin/win32/pdflatex.exe")
  #   print("Generating {}.tex".format(identifier))
  #   doc.generate_tex("../tex/{}".format(identifier))
  #   print("Done {}.".format(identifier))
  #   print("")























