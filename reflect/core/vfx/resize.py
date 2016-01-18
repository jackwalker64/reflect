# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import cv2
import copy



@clipMethod
def resize(clip, size = None, width = None, height = None):
  """resize(clip, size = None, width = None, height = None)

  Returns a copy of `clip` with the new frame dimensions.

  Examples
  --------
  >>> clip.resize((1280, 720))                 # 1280×720
  >>> clip.resize(0.5)                         # (0.5*oldWidth)×(0.5*oldHeight)
  >>> clip.resize(width = 1280)                # 1280×? where ? is computed automatically to preserve aspect ratio
  >>> clip.resize(height = 720)                # ?×720 where ? is computed automatically to preserve aspect ratio
  >>> clip.resize(width = 1280, height = 1024) # 1280×1024
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("resize requires a clip of type VideoClip")

  # Process the arguments
  (oldWidth, oldHeight) = clip.size
  if size != None:
    if width != None or height != None:
      raise TypeError("either specify size, or specify at least one of width and height")
    elif isinstance(size, int) or isinstance(size, float):
      (width, height) = (round(oldWidth * size), round(oldHeight * size))
    elif isinstance(size, tuple):
      (width, height) = size
    else:
      raise TypeError("size must be either an int, a float, or a (width, height) pair")
  else:
    if width != None and height != None:
      pass
    elif width != None and height == None:
      height = round(width / oldWidth * oldHeight)
    elif width == None and height != None:
      width = round(height / oldHeight * oldWidth)
    else:
      raise TypeError("resize requires either size, width, or height to be provided")

  # Source: A single VideoClip to be resized
  source = (clip,)

  # Metadata: Update the dimensions
  metadata = copy.copy(clip._metadata)
  metadata.size = (width, height)

  return ResizedVideoClip(source, metadata)



class ResizedVideoClip(VideoClip):
  """ResizedVideoClip(source, metadata)

  Represents a video clip that has had its frame width and height changed.
  """



  def __init__(self, source, metadata):
    super().__init__(source, metadata, isConstant = source[0]._isConstant)



  @memoizeHash
  def __hash__(self):
    return super().__hash__()



  def __eq__(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super().__eq__(other):
        return True

    return False



  def _framegen(self, n):
    image = self._source[0].frame(n)
    return cv2.resize(image, self.size, interpolation = cv2.INTER_AREA)
