# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import copy
import numpy
import cv2



@clipMethod
def greyscale(clip):
  """greyscale(clip)

  Returns a copy of `clip` where each pixel is grey with intensity 0.299 R + 0.587 G + 0.114 B.

  Examples
  --------
  >>> clip.greyscale()    # Returns a greyscale version of the clip
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("greyscale requires a clip of type VideoClip")

  # Source: A single VideoClip
  source = (clip,)

  # Metadata: Exactly the same as the base clip's
  metadata = copy.copy(clip._metadata)

  return GreyscaleVideoClip(source, metadata)



class GreyscaleVideoClip(VideoClip):
  """GreyscaleVideoClip(source, metadata)

  Represents a video clip where each pixel is grey with intensity 0.299 R + 0.587 G + 0.114 B.
  """



  def __init__(self, source, metadata):
    super().__init__(source, metadata, isConstant = source[0]._isConstant)



  @memoizeHash
  def __hash__(self):
    return super().__hash__()



  def _pseudoeq(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super()._pseudoeq(other):
        return True

    return False



  def __eq__(self, other):
    return self._pseudoeq(other) and self._source == other._source



  def _framegen(self, n):
    image = self._source[0].frame(n)

    grey = numpy.dot(image[:, :, :3], [0.299, 0.587, 0.114]).astype(numpy.uint8)
    w, h = grey.shape
    rgb = numpy.empty((w, h, 3), dtype = numpy.uint8)
    rgb[:, :, 2] = rgb[:, :, 1] = rgb[:, :, 0] = grey

    return rgb
