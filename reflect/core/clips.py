# -*- coding: utf-8 -*-

import fractions
import imageio
import os



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
