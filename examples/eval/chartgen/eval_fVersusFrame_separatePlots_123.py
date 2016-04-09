# -*- coding: utf-8 -*-

import numpy as np
from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, Plot, Figure, Package, Matrix
from pylatex.utils import italic
import os
import re
import math

if __name__ == "__main__":
  identifiers = ["eval1_longLoop", "eval2_longLoopChained", "eval3_longLoopChainedStepping"]

  def hitRatio(h, ncm, cm):
    h = h - 1
    if h <= 0 or h + ncm + cm == 0:
      return None
    else:
      return math.log10(h / (h + ncm + cm))

  def hitRatioN(h, ncm, cm):
    h = h - 1
    if h <= 0 or h + ncm == 0:
      return None
    else:
      return h / (h + ncm)

  series = [
    {
      "name": "h",
      "color": "blue",
      "function": (lambda h, ncm, cm: h - 1),
      "isLogScale": False,
      "yminmax": {}
    },
    # {
    #   "color": "red",
    #   "function": (lambda h, ncm, cm: ncm)
    # },
    # {
    #   "name": "math.log10(h / h + ncm + cm)",
    #   "color": "red",
    #   "function": hitRatio
    # },
    {
      "name": "math.log10(h / h + ncm)",
      "color": "orange",
      "function": hitRatioN,
      "isLogScale": True,
      "yminmax": {
        "eval1_longLoop": (0.228758, 1.1),
        "eval2_longLoopChained": (0.000186, 2),
        "eval3_longLoopChainedStepping": (0.008, 1.4),
      }
    },
    # {
    #   "color": "purple",
    #   "function": (lambda h, ncm, cm: 0 if ncm == 0 or h + ncm == 0 else ncm / (h + ncm))
    # },
    # {
    #   "color": "purple",
    #   "function": (lambda h, ncm, cm: 0 if ncm == 0 or h + ncm == 0 else math.log10(ncm / (h + ncm)))
    # },
    # {
    #   "color": "orange",
    #   "function": (lambda h, ncm, cm: -3 if ncm == 0 or h + ncm + cm == 0 else math.log10(ncm / (h + ncm + cm)))
    # }
  ]

  for identifier in identifiers:
    print("Preparing {}".format(identifier))

    doc = Document()
    doc.packages.append(Package("geometry", options = ["tmargin=1cm", "lmargin=1cm"]))

    for s in series:
      with doc.create(Section("Series: {}".format(s["name"]))):
        algorithms = ["fifo", "lru", "mru", "specialised"]
        # algorithms = ["mru", "specialised", "specialisedOrig"]
        data = { a: [] for a in algorithms }

        for algorithm in algorithms:
          with open("../logs/{}_{}.log".format(identifier, algorithm)) as f:
            t = 0
            for line in f:
              m = re.match(r"^INFO: Cache stats: (\d+) h / (\d+) ncm / (\d+) cm .*? hr$", line)
              if m is not None:
                h, ncm, cm = m.groups()
                h, ncm, cm = int(h), int(ncm), int(cm)
                if identifier == "eval3_longLoopChainedStepping":
                  if t >= 100:
                    data[algorithm].append((h, ncm, cm))
                else:
                  data[algorithm].append((h, ncm, cm))
                t += 1
          xmax = len(data[algorithm])

        xmin = -0.1 * xmax
        xmax *= 1.1

        if identifier in s["yminmax"]:
          ymin, ymax = s["yminmax"][identifier]
        else:
          ymin = min([min([s["function"](h, ncm, cm) for (h, ncm, cm) in data[algorithm] if s["function"](h, ncm, cm) is not None] + [float("inf")]) for algorithm in algorithms])
          ymax = max([max([s["function"](h, ncm, cm) for (h, ncm, cm) in data[algorithm] if s["function"](h, ncm, cm) is not None] + [float("-inf")]) for algorithm in algorithms])

          if ymin == float("inf"):
            ymin = 0
          if ymax == float("-inf"):
            ymax = 0

          if s["isLogScale"]:
            ymax, ymin = math.log10(ymax), math.log10(ymin)
          ygap = (ymax - ymin) / 10
          ymax += ygap
          ymin -= ygap
          if s["isLogScale"]:
            ymax, ymin = pow(10, ymax), pow(10, ymin)
          ymin, ymax = round(ymin, 6), round(ymax, 6)

        for algorithm in algorithms:
          currentData = data[algorithm]

          options = "title={}, height=5cm, width=5cm, grid=major, xmin=({}), xmax=({}), ymin=({}), ymax=({})".format(algorithm, xmin, xmax, ymin, ymax)
          if s["isLogScale"]:
            options = "ymode=log, " + options
            # , ytick={1,0.1,0.01,0.001, 0.0001, 0.00001, 0.000001}
          with doc.create(TikZ()):
            with doc.create(Axis(options = options)) as plot:
              color = s["color"]
              f = s["function"]

              coordinates = []
              for (t, (h, ncm, cm)) in enumerate(currentData):
                y = f(h, ncm, cm)
                if y is not None:
                  coordinates.append((t, y))

              plot.append(Plot(options = "very thick,color={}".format(color), coordinates = coordinates))

    print("Generating {}.pdf".format(identifier))
    doc.generate_pdf("../tex/{}".format(identifier), compiler = "D:/Software/texlive/bin/win32/pdflatex.exe")
    print("Generating {}.tex".format(identifier))
    doc.generate_tex("../tex/{}".format(identifier))
    print("Done {}.".format(identifier))
    print("")
