# -*- coding: utf-8 -*-

import logging
import fractions
import imageio
import os
import inspect

mode = "normal"



class Clip(object):
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
  """VideoClip(source, metadata)

  Represents a sequence of image frames.
  """



  def __init__(self, source, metadata):
    self._source = source
    self._metadata = metadata
    # self.audio = audio
    # self.mask = mask

    if type(self._source) == str:
      # This VideoClip is sourced directly from a file, so this clip belongs in the default graph
      from .util import CompositionGraph
      self._graph = CompositionGraph.current()
      self._graph.addLeaf(self)
    elif type(self._source) == tuple:
      # This VideoClip is sourced from one or more other clips, which are no longer leaves
      for clip in self._source:
        if clip._graph != self._source[0]._graph:
          raise Exception("the sources are not all in the same graph")
        if clip._graph.isLeaf(clip):
          clip._graph.removeLeaf(clip)

      # Add this new clip as a leaf in the graph containing the source(s)
      self._graph = self._source[0]._graph
      self._graph.addLeaf(self)
    else:
      raise TypeError("expected source to be of type str or tuple, but received an object of type {}".format(type(self._source)))



  def __hash__(self):
    return hash((self._source, self._metadata))



  def __eq__(self, other):
    return self._source == other._source and self._metadata == other._metadata



  @property
  def size(self):
    return self._metadata.size

  @property
  def duration(self):
    return self._metadata.duration

  @property
  def fps(self):
    return self._metadata.fps

  @property
  def width(self):
    return self._metadata.size[0]

  @property
  def height(self):
    return self._metadata.size[1]

  @property
  def aspectRatio(self):
    gcd = fractions.gcd(self.width, self.height)
    return (int(self.width / gcd), int(self.height / gcd))

  @property
  def frameCount(self):
    return round(self.duration * self.fps)



  def _framegen(self, n):
    # _framegen must be implemented in the subclass.
    raise NotImplementedError()



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
        image = self._framegen(n)
        cache.stage(self, n, image)
        return image
    else:
      # We are not in server mode, so there is no cache and we should just render the frame
      return self._framegen(n)



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



  def __eq__(self, other):
    return self.size == other.size and self.duration == other.duration and self.fps == other.fps
