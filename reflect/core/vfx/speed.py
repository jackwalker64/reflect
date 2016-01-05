# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
from ..util import timecodeToFrame
import copy



@clipMethod
def speed(clip, scale = None, duration = None, frameCount = None):
  """speed(clip, scale = None, duration = None, frameCount = None)

  Returns a copy of `clip` whose frames will be delivered at a different rate.

  The fps property of the clip will stay the same, but frames may be either duplicated or skipped.

  Specify `scale` to multiply the speed of the clip by some scale factor.
  Alternatively specify a new total clip `duration` or `frameCount` in order to compute `scale`
  automatically.

  Examples
  --------
  >>> clip.speed(2)                 # Half of `clip`'s frames are essentially discarded.
  >>> clip.speed(0.5)               # frame(2n) = frame(2n + 1).
  >>> clip.speed(duration = "2:00") # Computes a scale factor so that the new clip is 2 minutes long.
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("expected a clip of type VideoClip")

  if duration is not None:
    if scale is not None or frameCount is not None:
      raise TypeError("only one of scale, duration, frameCount should be specified")
    frameCount = timecodeToFrame(duration, clip.fps)

  if frameCount is not None:
    if scale is not None:
      raise TypeError("only one of scale, duration, frameCount should be specified")
    scale = clip.frameCount / frameCount

  if scale is None:
    raise TypeError("expected one of scale, duration, frameCount to be specified")

  # Source: A single VideoClip
  source = (clip,)

  # Metadata: Update the total number of frames and the fps
  metadata = copy.copy(clip._metadata)
  metadata.frameCount = int(metadata.frameCount / scale)

  return SpedVideoClip(source, metadata, scale = scale)



class SpedVideoClip(VideoClip):
  """SpedVideoClip(source, metadata, scale)

  Represents a video clip whose frame delivery rate has been changed.
  """



  def __init__(self, source, metadata, scale):
    super().__init__(source, metadata, isIndirection = True)

    self._scale = scale



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__(), self._scale))



  def __eq__(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super().__eq__(other):
        # The scale factors must be the same
        if self._scale == other._scale:
          return True

    return False



  def _framegen(self, n):
    return self._source[0].frame(int(n * self._scale))
