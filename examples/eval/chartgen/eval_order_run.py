# -*- coding: utf-8 -*-

import numpy
from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, Plot, Figure, Package, Matrix
from pylatex.utils import italic
import os
import re
import math

if __name__ == "__main__":
  identifiers = ["eval8_order_run_noopt", "eval8_order_run_opt"]

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
          m = re.match(r"^INFO: Accessed frame 1 in (.+?) us$", line)
          if m is not None:
            (a,) = m.groups()
            samples.append(float(a))
            if len(samples) == 3:
              sample = numpy.mean(samples) / 1000
              samples = []
              yvalues.append(sample)
      assert(len(yvalues) == 21)
      # xvalues = [1, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000]
      xvalues = [1, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400]
      xvalues = [x*x/1000000 for x in xvalues]
      coordinates[identifier] = zip(xvalues, yvalues[:len(xvalues)])

    options = "height=10cm, width=10cm, grid=major, xlabel=input frame size / megapixels, ylabel=render time per frame / ms"
    with doc.create(TikZ()):
      with doc.create(Axis(options = options)) as plot:
        for identifier in identifiers:
          color = {
            "eval8_order_run_noopt": "red",
            "eval8_order_run_opt": "blue"
          }[identifier]
          name = {
            "eval8_order_run_noopt": "no optimisation",
            "eval8_order_run_opt": "canonical order"
          }[identifier]
          plot.append(Plot(name = name, options = "very thick,color={}".format(color), coordinates = coordinates[identifier]))

    name = "eval8_order_run"
    # print("Generating {}.pdf".format(name))
    # doc.generate_pdf("../tex/{}".format(name), compiler = "D:/Software/texlive/bin/win32/pdflatex.exe")
    print("Generating {}.tex".format(name))
    doc.generate_tex("../tex/{}".format(name))
    print("Done {}.".format(name))
    print("")

    print("""Remember to change the start of the .tex file to:

\pgfplotsset{vasymptote/.style={
  before end axis/.append code={
    \draw[densely dashed] ({rel axis cs:0,0} -| {axis cs:#1,0})
    -- ({rel axis cs:0,1} -| {axis cs:#1,0});
  }
}}

\\begin{tikzpicture}
\\begin{axis}[height=10cm, width=10cm, grid=major, xlabel=input frame size / megapixels, ylabel=render time per frame / ms, vasymptote=0.2916]""")






















