# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import copy



@clipMethod
def rate(clip, fps = None, delay = None):
  """rate(clip, fps = None, delay = None)

  Returns a copy of `clip` with a different fps value.

  Either specify the new number of frames per second with `fps`, or specify a `delay` (number of
  seconds per frame) to compute `fps` automatically.

  Examples
  --------
  >>> clip.rate(30)           # Sets the fps to 30
  >>> clip.rate(delay = 0.04) # Each frame will last for 0.04 seconds, i.e. the new fps value is 25
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("expected a clip of type VideoClip")

  if delay is not None:
    if fps is not None:
      raise TypeError("only one of either fps or delay should be specified")
    fps = 1.0 / delay

  if fps is None:
    raise TypeError("expected one of fps or delay to be specified")

  # Source: A single VideoClip
  source = (clip,)

  # Metadata: Update the total number of frames and the fps
  metadata = copy.copy(clip._metadata)
  metadata.fps = float(fps)

  return ChangedRateVideoClip(source, metadata)



class ChangedRateVideoClip(VideoClip):
  """ChangedRateVideoClip(source, metadata)

  Represents a video clip whose fps property has been changed.
  """



  def __init__(self, source, metadata):
    super().__init__(source, metadata, isIndirection = True, isConstant = source[0]._isConstant)



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
    return self._source[0].frame(n)
