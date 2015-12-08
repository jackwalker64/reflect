# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import copy



@clipMethod
def speed(clip, scale = None, fps = None, delay = None):
  """speed(clip, scale = None, fps = None, delay = None)

  Returns a copy of `clip` whose frames will be delivered at a different rate.

  Examples
  --------
  >>> clip.speed(2)        # Half of `clip`'s frames are essentially discarded.
  >>> clip.speed(0.5)      # frame(2n) = frame(2n + 1).
  >>> clip.speed(fps = 60) # If the previous fps was lower than 60 then some frames will be repeated.
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("expected a clip of type VideoClip")

  if scale is not None:
    if fps is not None or delay is not None:
      raise TypeError("only one of scale, fps, delay should be specified")
    fps = clip.fps
  elif fps is not None:
    if delay is not None:
      raise TypeError("only one of scale, fps, delay should be specified")
    scale = clip.fps / fps
  elif delay is not None:
    fps = 1.0 / delay
    scale = 1.0
  else:
    raise TypeError("expected one of scale, fps, delay to be specified")

  # Source: A single VideoClip
  source = (clip,)

  # Metadata: Update the total number of frames and the fps
  metadata = copy.copy(clip._metadata)
  metadata.frameCount = int(metadata.frameCount / scale)
  metadata.fps = float(fps)

  return SpeedVideoClip(source, metadata, scale = scale)



class SpeedVideoClip(VideoClip):
  """SpeedVideoClip(source, metadata, scale)

  Represents a video clip whose frame delivery rate has been changed.
  """



  def __init__(self, source, metadata, scale):
    super().__init__(source, metadata)

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
