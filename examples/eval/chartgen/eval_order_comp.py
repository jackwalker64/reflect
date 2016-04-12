# -*- coding: utf-8 -*-

import numpy
from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, Plot, Figure, Package, Matrix
from pylatex.utils import italic
import os
import re
import math

if __name__ == "__main__":
  identifiers = ["eval9_order_comp_noopt", "eval9_order_comp_opt"]

  doc = Document()
  doc.packages.append(Package("geometry", options = ["tmargin=1cm", "lmargin=1cm"]))

  with doc.create(Section("Stuff")):
    coordinates = {}
    for identifier in identifiers:
      print("Preparing {}".format(identifier))
      yvalues = []
      with open("../logs/{}.log".format(identifier)) as f:
        samples = []
        for line in f:
          m = re.match(r"^INFO: Compilation took (.+?) s$", line)
          if m is not None:
            (a,) = m.groups()
            samples.append(float(a))
            if len(samples) == 6:
              sample = numpy.mean(samples[1:])
              samples = []
              yvalues.append(sample)
      assert(len(yvalues) == 11)
      xvalues = [5, 41, 81, 121, 161, 201, 241, 281, 321, 361, 401]
      coordinates[identifier] = zip(xvalues, yvalues)

    options = "height=10cm, width=10cm, grid=major, xlabel=number of input nodes $N$, ylabel=total compile time / s"
    with doc.create(TikZ()):
      with doc.create(Axis(options = options)) as plot:
        for identifier in identifiers:
          color = {
            "eval9_order_comp_noopt": "red",
            "eval9_order_comp_opt": "blue"
          }[identifier]
          name = {
            "eval9_order_comp_noopt": "no optimisation",
            "eval9_order_comp_opt": "canonical order"
          }[identifier]
          plot.append(Plot(name = name, options = "very thick,color={}".format(color), coordinates = coordinates[identifier]))

    name = "eval9_order_comp"
    # print("Generating {}.pdf".format(name))
    # doc.generate_pdf("../tex/{}".format(name), compiler = "D:/Software/texlive/bin/win32/pdflatex.exe")
    print("Generating {}.tex".format(name))
    doc.generate_tex("../tex/{}".format(name))
    print("Done {}.".format(name))
    print("")
























