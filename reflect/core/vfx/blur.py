# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import cv2
import copy



@clipMethod
def blur(clip, size = None, width = None, height = None):
  """blur(clip, size = None, width = None, height = None)

  Returns a copy of `clip` where every frame has been blurred by the specified size.

  Examples
  --------
  >>> clip.blur(5)                       # blur by 5
  >>> clip.blur(width = 5)               # blur by 5 only in the horizontal direction
  >>> clip.blur((10, 5))                 # blur by 10 horizontally, and 5 vertically
  >>> clip.blur(width = 10, height = 5)) # blur by 10 horizontally, and 5 vertically
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("blur requires a clip of type VideoClip")

  # Process the arguments
  if size is not None:
    if width is not None or height is not None:
      raise TypeError("either specify size, or specify at least one of width and height")
    elif isinstance(size, int):
      (width, height) = (size, size)
    elif isinstance(size, tuple):
      (width, height) = size
    else:
      raise TypeError("size must be either an int or a (width, height) pair")
  else:
    if width is not None and height is not None:
      pass
    elif width is not None and height is None:
      height = 1
    elif width is None and height is not None:
      width = 1
    else:
      raise TypeError("either size, width, or height must be provided")

  if not isinstance(width, int) or not isinstance(height, int) or width < 1 or height < 1:
    raise ValueError("blur amounts must be integers greater than or equal to 1")

  # Source: A single VideoClip to be blurred
  source = (clip,)

  # Metadata: Exactly the same as the base clip's
  metadata = copy.copy(clip._metadata)

  return BlurredVideoClip(source, metadata, (width, height))



class BlurredVideoClip(VideoClip):
  """BlurredVideoClip(source, metadata, size)

  Represents a video clip that has had each of its frames blurred.
  """



  def __init__(self, source, metadata, size):
    super().__init__(source, metadata, isConstant = source[0]._isConstant)

    self._blurSize = size



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__(), self._blurSize))



  def _pseudoeq(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super()._pseudoeq(other):
        # The blur size must be the same
        if self._blurSize == other._blurSize:
          return True

    return False



  def __eq__(self, other):
    return self._pseudoeq(other) and self._source == other._source



  def _framegen(self, n):
    image = self._source[0].frame(n)
    return cv2.blur(image, self._blurSize)
