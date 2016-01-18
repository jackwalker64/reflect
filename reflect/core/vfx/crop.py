# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import copy



@clipMethod
def crop(clip, x1 = None, y1 = None, x2 = None, y2 = None, xc = None, yc = None, width = None, height = None):
  """crop(clip, x1 = None, y1 = None, x2 = None, y2 = None, xc = None, yc = None, width = None, height = None)

  Returns a rectangular subregion of `clip`.

  Examples
  --------
  >>> clip.crop(x1 = 100, y1 = 100, x2 = 300, y2 = 200)        # conserves a 200×100 region with the top-left pixel at (100, 100)
  >>> clip.crop(x1 = clip.width / 2)                           # conserves the right-hand half of the clip
  >>> clip.crop(xc = 960, yc = 540, width = 100, height = 100) # conserves a 100×100 box centred about (960, 540)
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("crop requires a clip of type VideoClip")

  # If width was passed as an argument, then use it to deduce x1 and/or x2
  if width is not None:
    if x1 is not None:
      if x2 is not None:
        if x1 + width != x2:
          raise ValueError("inconsistent arguments: x1 = {}, x2 = {}, width = {}".format(x1, x2, width))
      else:
        x2 = x1 + width
    elif x2 is not None:
      x1 = x2 - width
    elif xc is not None:
      x1 = xc - width / 2
      x2 = xc + width / 2
    else:
      x1 = 0
      x2 = width

  # If height was passed as an argument, then use it to deduce y1 and/or y2
  if height is not None:
    if y1 is not None:
      if y2 is not None:
        if y1 + height != y2:
          raise ValueError("inconsistent arguments: y1 = {}, y2 = {}, height = {}".format(y1, y2, height))
      else:
        y2 = y1 + height
    elif y2 is not None:
      y1 = y2 - height
    elif yc is not None:
      y1 = yc - height / 2
      y2 = yc + height / 2
    else:
      y1 = 0
      y2 = height

  if x1 is None:
    x1 = 0
  if y1 is None:
    y1 = 0
  if x2 is None:
    x2 = clip.width
  if y2 is None:
    y2 = clip.height

  x1 = int(x1)
  y1 = int(y1)
  x2 = int(x2)
  y2 = int(y2)

  # Check that the user-specified region is within the source clip's boundaries
  if x1 < 0:
    raise ValueError("the crop region exceeds the clip's left boundary by {} pixels (x1 = {})".format(-x1, x1))
  if y1 < 0:
    raise ValueError("the crop region exceeds the clip's top boundary by {} pixels (y1 = {})".format(-y1, y1))
  if x2 > clip.width:
    raise ValueError("the crop region exceeds the clip's right boundary by {} pixels (x2 = {})".format(x2 - clip.width, x2))
  if y2 > clip.height:
    raise ValueError("the crop region exceeds the clip's bottom boundary by {} pixels (y2 = {})".format(y2 - clip.height, y2))

  # Source: A single VideoClip to be cropped
  source = (clip,)

  # Metadata: Update the dimensions
  metadata = copy.copy(clip._metadata)
  metadata.size = (x2 - x1, y2 - y1)

  return CroppedVideoClip(source, metadata, x1 = x1, y1 = y1, x2 = x2, y2 = y2)



class CroppedVideoClip(VideoClip):
  """CroppedVideoClip(source, metadata, x1, y1, x2, y2)

  Represents a subregion of a video clip.
  """



  def __init__(self, source, metadata, x1, y1, x2, y2):
    super().__init__(source, metadata, isIndirection = True)

    self._x1 = x1
    self._y1 = y1
    self._x2 = x2
    self._y2 = y2



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__(), (self._x1, self._y1, self._x2, self._y2)))



  def __eq__(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super().__eq__(other):
        # The crop regions must be the same
        if (self._x1, self._y1, self._x2, self._y2) == (other._x1, other._y1, other._x2, other._y2):
          return True

    return False



  def _framegen(self, n):
    image = self._source[0].frame(n)
    return image[self._y1:self._y2, self._x1:self._x2]
