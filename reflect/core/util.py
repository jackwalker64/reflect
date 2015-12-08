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
    return globals()["currentGraph"]



  @staticmethod
  def reset():
    """reset()

    Discard the current graph and initialise a new, empty graph.
    """

    globals()["currentGraph"] = CompositionGraph()



  @staticmethod
  def swap(newGraph):
    """swap(newGraph)

    Sets the current global graph to `newGraph`, and returns the old graph.
    """

    oldGraph = globals()["currentGraph"]
    globals()["currentGraph"] = newGraph
    return oldGraph



  def __init__(self):
    self.leaves = set()



  def addLeaf(self, clip):
    """addLeaf(clip)

    Add `clip` to the graph as a leaf.
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



def timecodeToFrame(t, fps):
  """timecodeToFrame(t, fps)

  Converts the timecode `t` to an integer frame number.

  The timecode can either be an int/float number of seconds, or a string "[[h:]m:]s".
  """

  if isinstance(t, int) or isinstance(t, float):
    return int(t * fps)

  if not isinstance(t, str):
    raise TypeError("expected a timecode of type int, float, or str, but instead received a {}".format(type(t)))

  # Parse the timecode string
  h = 0.0
  m = 0.0
  s = 0.0
  parts = t.split(":")
  try:
    if len(parts) == 1:
      s = float(parts[0])
    elif len(parts) == 2:
      m = float(parts[0]) # Realistically, m (and h) will be nonnegative integers, but allow them to be floats anyway
      s = float(parts[1])
    elif len(parts) == 3:
      h = float(parts[0])
      m = float(parts[1])
      s = float(parts[2])
    else:
      raise ValueError("invalid timecode: {}".format(t))
  except ValueError as e:
    raise ValueError("invalid timecode: {}".format(t)) from None

  # Calculate the total number of seconds represented by the timecode
  totalSeconds = s + m * 60 + h * 60 * 60

  return int(totalSeconds * fps)
