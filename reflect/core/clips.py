# -*- coding: utf-8 -*-

import logging
import fractions
import imageio
import os
import inspect

mode = "normal"



class Clip:
  """Clip()

  This is the base class from which VideoClip, AudioClip etc. are derived.
  """



  def __init__(self):
    pass



  def fx(self, f, *args, **kwargs):
    """fx(f, *args, **kwargs)

    >>> clip.fx(f, *args, **kwargs)
    is equivalent to
    >>> f(clip, *args, **kwargs)

    Useful for chaining custom effects.

    Alternatively you may bind custom effect functions to the relevant class, e.g.
    >>> VideoClip.f = f
    and then use it by calling
    >>> clip.f(*args, **kwargs)
    """

    return f(self, *args, **kwargs)



class VideoClip(Clip):
  """VideoClip()

  Represents a sequence of image frames.
  """



  def __init__(self, source, framegen, metadata):
    self.source = source
    self.framegen = framegen
    self.metadata = metadata
    # self.audio = audio
    # self.mask = mask

    if type(self.source) == str:
      # This VideoClip is sourced directly from a file, so this clip belongs in the default graph
      from .util import CompositionGraph
      self.graph = CompositionGraph.current()
      self.graph.addLeaf(self)
    elif type(self.source) == tuple:
      # This VideoClip is sourced from one or more other clips, which are no longer leaves
      for clip in self.source:
        if clip.graph != self.source[0].graph:
          raise Exception("the sources are not all in the same graph")
        if clip.graph.isLeaf(clip):
          clip.graph.removeLeaf(clip)

      # Add this new clip as a leaf in the graph containing the source(s)
      self.graph = self.source[0].graph
      self.graph.addLeaf(self)
    else:
      raise TypeError("expected source to be of type str or tuple, but received an object of type {}".format(type(self.source)))

    # Initialise this VideoClip's internal store of cached frames
    self.store = {}



  def __hash__(self):
    """__hash__(self)

    Two VideoClips have the same hash if their framegen closures are "equivalent", i.e. they have
    the same source code and the same local variables.
    """

    def subhash(o):
      """subhash(o)

      The purpose of this function is to provide custom hashing functions for various classes,
      without overriding the actual classes' definitions of __hash__.

      This function will usually return o.__hash__(), but for some types of o, the hashing
      behaviour will be weaker.
      """

      if isinstance(o, imageio.core.Format.Reader):
        # Readers should have the same hash if they are readers of the same filepath
        return hash(o.request.filename)
      else:
        return hash(o)

    closureVarsDict = inspect.getclosurevars(self.framegen).nonlocals
    closureVarsTuple = tuple((varName, subhash(closureVarsDict[varName])) for varName in closureVarsDict)
    closureSourceCode = inspect.getsource(self.framegen)

    return hash((closureSourceCode, closureVarsTuple))



  def __eq__(self, other):
    """__eq__(self)

    Two VideoClips are equal iff their framegen closures are "equivalent", i.e. they have the same
    source code and the same local variables.
    """

    def subeq(a, b):
      """subeq(a, b)

      The purpose of this function is to provide custom equality functions for various classes,
      without overriding the actual classes' definitions of __eq__.

      This function will usually return a == b, but for some types of object, the behaviour will
      be weaker.
      """

      if isinstance(a, imageio.core.Format.Reader) and isinstance(b, imageio.core.Format.Reader):
        # Readers should be equal iff they are readers of the same filepath
        return a.request.filename == b.request.filename
      else:
        return a == b

    # Check that the source code is the same
    if inspect.getsource(self.framegen) != inspect.getsource(other.framegen):
      return False

    # Check that the closure variable names are equal
    closureVarsDictSelf = inspect.getclosurevars(self.framegen).nonlocals
    closureVarsDictOther = inspect.getclosurevars(other.framegen).nonlocals
    if sorted(closureVarsDictSelf.keys()) != sorted(closureVarsDictOther.keys()):
      return False

    # Check that the closure variable values are equal
    return all([subeq(closureVarsDictSelf[varName], closureVarsDictOther[varName]) for varName in closureVarsDictSelf])



  @property
  def size(self):
    return self.metadata.size

  @property
  def duration(self):
    return self.metadata.duration

  @property
  def fps(self):
    return self.metadata.fps

  @property
  def width(self):
    return self.metadata.size[0]

  @property
  def height(self):
    return self.metadata.size[1]

  @property
  def aspectRatio(self):
    gcd = fractions.gcd(self.width, self.height)
    return (int(self.width / gcd), int(self.height / gcd))

  @property
  def frameCount(self):
    return round(self.duration * self.fps)



  def frame(self, n):
    if mode == "server":
      from reflect.server.cache import Cache
      cache = Cache.current()
      image = cache.get(self, n, None)
      if image is not None:
        # The frame already exists in the cache, so don't bother re-rendering it
        return image
      else:
        # Render the frame, add it to the staging area of the cache, and then return it
        image = self.framegen(n)
        cache.stage(self, n, image)
        return image
    else:
      # We are not in server mode, so there is no cache and we should just render the frame
      return self.framegen(n)



class VideoClipMetadata():
  """VideoClipMetadata()

  Contains various properties representing the metadata of a particular video clip.
  """



  def __init__(self, size, duration, fps):
    self.size = size         # (width, height) in pixels
    self.duration = duration # duration in seconds
    self.fps = fps           # frames per second



  def __hash__(self):
    return hash((self.size, self.duration, self.fps))



def load(filepath):
  """load(filepath)

  Constructs and returns a Clip object representing the media at `filepath`.
  The type of Clip returned depends on the kind of file.
  """

  if not os.path.exists(filepath):
    raise IOError("The file \"{}\" does not exist.".format(os.path.realpath(filepath)))

  # (currently assuming the file is a video file)
  reader = imageio.get_reader(filepath)

  source = filepath

  def framegen(n):
    return reader.get_data(n)

  md = reader.get_meta_data()
  metadata = VideoClipMetadata(md["size"], md["duration"], md["fps"])

  return VideoClip(source, framegen, metadata)
