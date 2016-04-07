# -*- coding: utf-8 -*-

import numpy as np
from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, Plot, Figure, Package, Matrix
from pylatex.utils import italic
import os
import re
import math

if __name__ == "__main__":
  identifiers = ["eval1_longLoop", "eval2_longLoopChained"]

  series = [
    {
      "color": "blue",
      "function": (lambda h, ncm, cm: h)
    },
    # {
    #   "color": "red",
    #   "function": (lambda h, ncm, cm: ncm)
    # },
    {
      "color": "red",
      "function": (lambda h, ncm, cm: 0 if h == 0 or h + ncm + cm == 0 else math.log10(h / (h + ncm + cm)))
    },
    {
      "color": "purple",
      "function": (lambda h, ncm, cm: 0 if ncm == 0 or h + ncm == 0 else ncm / (h + ncm))
    },
    {
      "color": "purple",
      "function": (lambda h, ncm, cm: 0 if ncm == 0 or h + ncm == 0 else math.log10(ncm / (h + ncm)))
    },
    # {
    #   "color": "orange",
    #   "function": (lambda h, ncm, cm: -3 if ncm == 0 or h + ncm + cm == 0 else math.log10(ncm / (h + ncm + cm)))
    # }
  ]

  for identifier in identifiers:
    print("Preparing {}".format(identifier))

    doc = Document()
    doc.packages.append(Package("geometry", options = ["tmargin=1cm", "lmargin=1cm"]))

    with doc.create(Section("Charts")):
      for s in series:
        algorithms = ["fifo", "lru", "mru", "specialised"]
        # algorithms = ["mru", "specialised", "specialisedOrig"]
        data = { a: [] for a in algorithms }
        ymax = 0

        for algorithm in algorithms:
          with open("../logs/{}_{}.log".format(identifier, algorithm)) as f:
            for line in f:
              m = re.match(r"^INFO: Cache stats: (\d+) h / (\d+) ncm / (\d+) cm .*? hr$", line)
              if m is not None:
                h, ncm, cm = m.groups()
                h, ncm, cm = int(h), int(ncm), int(cm)
                ymax = max(ymax, h, ncm, cm)
                data[algorithm].append((h, ncm, cm))
          # data[algorithm] = data[algorithm][:400]
          xmax = len(data[algorithm]) + 50

        ymin = min([min([s["function"](h, ncm, cm) for (h, ncm, cm) in data[algorithm]]) for algorithm in algorithms])
        ymax = max([max([s["function"](h, ncm, cm) for (h, ncm, cm) in data[algorithm]]) for algorithm in algorithms])
        if ymin < 0:
          ymin *= 1.1
        else:
          ymin *= 0.9
        if ymax > 0:
          ymax *= 1.1
        else:
          ymax *= 0.9
        ymin, ymax = int(ymin), int(ymax)

        for algorithm in algorithms:
          currentData = data[algorithm]
          options = "title={}, height=5cm, width=5cm, grid=major, xmin=(-50), xmax=({}), ymin=({}), ymax=({})".format(algorithm, xmax, ymin, ymax)
          with doc.create(TikZ()):
            with doc.create(Axis(options = options)) as plot:
              color = s["color"]
              f = s["function"]
              coordinates = [(t, f(h, ncm, cm)) for (t, (h, ncm, cm)) in enumerate(currentData)]
              plot.append(Plot(options = "very thick,color={}".format(color), coordinates = coordinates))

    print("Generating {}.pdf".format(identifier))
    doc.generate_pdf("../tex/{}".format(identifier), compiler = "D:/Software/texlive/bin/win32/pdflatex.exe")
    print("Generating {}.tex".format(identifier))
    doc.generate_tex("../tex/{}".format(identifier))
    print("Done {}.".format(identifier))
    print("")
