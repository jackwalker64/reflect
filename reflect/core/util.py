# -*- coding: utf-8 -*-

from .clips import Clip



class CompositionGraph:
  """CompositionGraph()

  This class holds a set of leaf nodes, each an instance of the Clip class.
  The [directed acyclic] graph describes the dependencies between Clips.
  Clips are responsible (on construction) for updating the CompositionGraph they are in.
  The graph can be explored from its leaves.

  At any point in time, there is exactly one active composition graph, accessible via the static
  `current` method. Usually it can be left untouched, but it may be swapped in order to enable
  advanced manipulation of multiple distinct graphs.
  """



  @staticmethod
  def current():
    return currentGraph



  @staticmethod
  def swap(newGraph):
    """swap(newGraph)

    Sets the current global graph to `newGraph`, and returns the old graph.
    """

    oldGraph = currentGraph
    currentGraph = newGraph
    return oldGraph



  def __init__(self):
    self.leaves = set()



  def addLeaf(self, clip):
    """addLeaf(clip)

    Add `clip` as a leaf of the graph.
    """

    if not isinstance(clip, Clip):
      raise TypeError("clip must be an instance of Clip")

    self.leaves.add(clip)



  def removeLeaf(self, clip):
    """removeLeaf(clip)

    Remove `clip` from the set of leaves.
    Raises KeyError if `clip` was not present as a leaf of the graph.
    """

    if not isinstance(clip, Clip):
      raise TypeError("clip must be an instance of Clip")

    try:
      self.leaves.remove(clip)
    except:
      raise LookupError("clip was not found in the graph") from None



  def isLeaf(self, clip):
    """isLeaf(clip)

    Returns True if clip is in the set of leaves, and False otherwise.
    """

    if not isinstance(clip, Clip):
      raise TypeError("clip must be an instance of Clip")

    return clip in self.leaves



# Initialise an empty graph for normal use
currentGraph = CompositionGraph()
