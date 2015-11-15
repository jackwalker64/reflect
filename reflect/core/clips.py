# -*- coding: utf-8 -*-

import logging
import fractions
import imageio
import os

mode = "server" # this should initially be "normal"
logging.basicConfig(format = "%(levelname)s: %(message)s", level = logging.NOTSET)



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
    and then use it by
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
        clip.graph.removeLeaf(clip)

      # Add this new clip as a leaf in the graph containing the source(s)
      self.graph = self.source[0].graph
      self.graph.addLeaf(self)

    # Initialise this VideoClip's internal store of cached frames
    self.store = {}



  @property
  def size(self):
    return self.metadata["size"]

  @property
  def duration(self):
    return self.metadata["duration"]

  @property
  def fps(self):
    return self.metadata["fps"]

  @property
  def width(self):
    return self.metadata["size"][0]

  @property
  def height(self):
    return self.metadata["size"][1]

  @property
  def aspectRatio(self):
    gcd = fractions.gcd(self.width, self.height)
    return (int(self.width / gcd), int(self.height / gcd))

  @property
  def frameCount(self):
    return round(self.duration * self.fps)



  def frame(self, n):
    if mode == "server":
      if n in self.store:
        # The frame already exists in this clip's internal store, so don't bother re-rendering it
        logging.info("Store hit for frame {}".format(n))
        return self.store[n]
      else:
        # Render the frame and add it to the store before returning it
        logging.info("Rendering and storing frame {}".format(n))
        image = self.framegen(n)
        self.store[n] = image
        return image
    else:
      # We are not in server mode, so there is no internal store and we should just render the frame
      logging.info("Rendering frame {}".format(n))
      return self.framegen(n)



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
  metadata = {
    "size":     md["size"], # (width, height) in pixels
    "duration": md["duration"], # duration in seconds
    "fps":      md["fps"]
  }

  return VideoClip(source, framegen, metadata)
