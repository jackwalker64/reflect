# -*- coding: utf-8 -*-

from .clips import Clip
import time
import logging



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
    self.forced = set()



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



  def addForcedPreviewNode(self, clip):
    """addForcedPreviewNode(clip)

    Add `clip` as a node to be previewed, regardless of whether or not it is a leaf.
    """

    if not isinstance(clip, Clip):
      raise TypeError("clip must be an instance of Clip")

    self.forced.add(clip)



  def unifyPreviewNodes(self):
    """unifyPreviewNodes()

    Move the forced preview nodes in to the set of leaves.
    """

    self.leaves.update(self.forced)
    self.forced = set()



  def flattenConcats(self):
    if self.forced:
      raise Exception("Attempted to flatten concats before unifying the preview nodes")

    from . import vfx

    def sourcesOf(clip):
      q = list(reversed(clip._source))
      while q:
        s = q.pop()
        if isinstance(s, vfx.concat.ConcatenatedVideoClip):
          q.extend(reversed(s._source))
        else:
          yield s

    ta1 = time.perf_counter()

    leaves = set(self.leaves)
    leavesToRemove = []
    for leaf in leaves:
      if isinstance(leaf, vfx.concat.ConcatenatedVideoClip):
        # Compute the flat source tuple of the leaf
        finalSources = tuple(sourcesOf(leaf))

        # If the concat wasn't already flat, then add it to the DAG
        if finalSources != leaf._source:
          newLeaf = finalSources[0].concat(finalSources[1:])
          newLeaf._timestamp = leaf.timestamp
          leavesToRemove.append(leaf)
    for leaf in leavesToRemove:
      self.removeLeaf(leaf)

    ta2 = time.perf_counter()
    logging.info("Concat flattening took {0:.16f} s".format(ta2 - ta1))



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

  if t[0] == "-":
    negative = -1
    t = t[1:]
  else:
    negative = 1

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

  return negative * round(totalSeconds * fps)



def frameToTimecode(n, fps):
  """frameToTimecode(n, fps)

  Converts the integer frame number `n` to a timecode "h:m:s".
  """

  if n < 0:
    prefix = "-"
    n = -n
  else:
    prefix = ""

  (h, m_) = divmod(n, fps * 60 * 60)
  (m, s_) = divmod(m_, fps * 60)
  s = s_ / fps

  return "{0}{1:0>2.0f}:{2:0>2.0f}:{3:0>5.2f}".format(prefix, h, m, s)



def interpretSubclipParameters(n1, n2, frameCount):
  """interpretSubclipParameters(n1, n2, frameCount)

  Converts (n1, n2) to be in the range [0, frameCount) and raises a ValueError if the parameters
  are invalid.
  """

  if n1 < 0:
    n1 += frameCount
  if n2 < 0:
    n2 += frameCount
  if n1 > n2 or n1 < 0 or n1 >= frameCount or n2 < 1 or n2 > frameCount:
    raise ValueError("invalid subclip parameters: n1 = {}, n2 = {}, clip.frameCount = {}".format(n1, n2, frameCount))

  return (n1, n2)
