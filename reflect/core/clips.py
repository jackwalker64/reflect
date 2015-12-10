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



  def __init__(self, isIndirection = False):
    self.cacheEntry = None

    # If this clip doesn't actually apply changes to its source frames (as is the case with e.g.
    # subclip, concat) then this clip's frames shouldn't be cached.
    self._isIndirection = isIndirection



  def __str__(self):
    # Debug method, allowing the user to give readable names to nodes by setting the _str property
    try:
      return self._str
    except Exception as _:
      return self.__class__.__name__



  @property
  def isIndirection(self):
    return self._isIndirection



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



def memoizeHash(f):
  """@memoizeHash

  A simple decorator for permanently caching the result of __hash__.
  """

  def wrapper(self):
    if not hasattr(self, "_memoizedHash"):
      # __hash__ hasn't been called before on this instance.
      self._memoizedHash = f(self)
    return self._memoizedHash

  return wrapper



def clipMethod(f):
  """@clipMethod

  A decorator that calls f to construct a new clip, but additionally adds the new clip to the
  appropriate CompositionGraph.
  """

  def wrapper(*args, **kwargs):
    # Construct the clip
    clip = f(*args, **kwargs)

    # Before returning clip, add it to the appropriate graph
    if isinstance(clip._source, str):
      # This Clip is sourced directly from a file, so this clip belongs in the default graph
      from .util import CompositionGraph
      clip._graph = CompositionGraph.current()
      clip._graph.addLeaf(clip)
    elif isinstance(clip._source, tuple):
      # This Clip is sourced from one or more other clips, which are no longer leaves
      for sourceClip in clip._source:
        if sourceClip._graph != clip._source[0]._graph:
          raise Exception("the sources are not all in the same graph")
        if sourceClip._graph.isLeaf(sourceClip):
          sourceClip._graph.removeLeaf(sourceClip)

      # Add this new clip as a leaf in the graph containing the source(s)
      clip._graph = clip._source[0]._graph
      clip._graph.addLeaf(clip)
    else:
      raise TypeError("expected source to be of type str or tuple, but received an object of type {}".format(type(clip._source)))

    return clip

  return wrapper



class VideoClip(Clip):
  """VideoClip(source, metadata)

  Represents a sequence of image frames.
  """



  def __init__(self, source, metadata, isIndirection = False):
    # The hash of self can only be computed after calling Clip.__init__(self)
    super().__init__(isIndirection = isIndirection)

    self._source = source
    self._metadata = metadata
    # self.audio = audio
    # self.mask = mask



  @memoizeHash
  def __hash__(self):
    return hash((self._source, self._metadata))



  def __eq__(self, other):
    return self._source == other._source and self._metadata == other._metadata



  @property
  def size(self):
    return self._metadata.size

  @property
  def duration(self):
    return self.frameCount / self.fps

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
    return self._metadata.frameCount



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
        # Render the frame, offer it to the cache, and then return it
        image = self._framegen(n)
        cache.set(self, n, image)
        return image
    else:
      # We are not in server mode, so there is no cache and we should just render the frame
      return self._framegen(n)



  def save(self, filepath, **kwargs):
    options = {
      "uri": filepath,
      "format": "FFMPEG",
      "mode": "I",
      "fps": self.fps,
      "ffmpeg_params": []
    }

    if "codec" in kwargs:
      options["codec"] = kwargs["codec"]
    else:
      options["codec"] = "libx264"

    if "pixelformat" in kwargs:
      options["pixelformat"] = kwargs["pixelformat"]
    else:
      options["pixelformat"] = "yuv420p"

    if "quality" in kwargs:
      options["quality"] = kwargs["quality"]
    elif "bitrate" in kwargs:
      options["bitrate"] = kwargs["bitrate"]
    elif "crf" in kwargs:
      options["ffmpeg_params"].extend(["-crf", str(kwargs["crf"])])
    else:
      options["ffmpeg_params"].extend(["-crf", "30"])

    if "ffmpegParams" in kwargs:
      options["ffmpeg_params"].extend(kwargs["ffmpegParams"])

    writer = imageio.get_writer(**options)
    for i in range(0, self.frameCount):
      im = self.frame(i)
      writer.append_data(im)
    writer.close()



class VideoClipMetadata():
  """VideoClipMetadata()

  Contains various properties representing the metadata of a particular video clip.
  """



  def __init__(self, size, frameCount, fps):
    self.size = size             # (width, height) in pixels
    self.frameCount = frameCount # total number of frames
    self.fps = fps               # frames per second



  def __hash__(self):
    return hash((self.size, self.frameCount, self.fps))



  def __eq__(self, other):
    return self.size == other.size and self.frameCount == other.frameCount and self.fps == other.fps
