# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import copy



@clipMethod
def reverse(clip):
  """reverse(clip)

  Returns `clip` with its frames in the reverse order.

  Examples
  --------
  >>> clip.reverse()   # frame 0 becomes frame (clip.frameCount - 1) etc
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("expected a clip of type VideoClip")

  source = (clip,)
  metadata = copy.copy(clip._metadata)

  return ReversedVideoClip(source, metadata)



class ReversedVideoClip(VideoClip):
  """ReversedVideoClip(source, metadata, n1, n2)

  Represents a clip with its frames in the reverse order.
  """



  def __init__(self, source, metadata):
    super().__init__(source, metadata, isIndirection = True, isConstant = source[0]._isConstant)



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__()))



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
    clip = self._source[0]

    image = clip.frame(clip.frameCount - n - 1)

    return image
