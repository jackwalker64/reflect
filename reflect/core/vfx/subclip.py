# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
from ..util import timecodeToFrame
import copy



@clipMethod
def subclip(clip, n1 = None, n2 = None, frameCount = None, t1 = None, t2 = None, duration = None):
  """subclip(clip, n1 = None, n2 = None, frameCount = None, t1 = None, t2 = None, duration = None)

  Returns a contiguous subsequence of the frames of `clip`.

  The subsequence can be specified either by timecodes (t1 and/or t2 and/or duration),
  or by frame numbers (n1 and/or n2 and/or frameCount).

  Examples
  --------
  >>> clip.subclip(10)               # Conserves frames after the 10 second mark
  >>> clip.subclip("01:00", 5)       # Produces a 5 second clip starting at 1 minute in
  >>> clip.subclip(n1 = 42, n2 = 52) # Produces a clip containing only 10 frames (42..51 inclusive)
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("expected a clip of type VideoClip")

  # Convert timecodes
  if t1 is not None:
    if n1 is not None:
      raise TypeError("expected at most one of t1 and n1, but received both")
    else:
      n1 = timecodeToFrame(t1, clip.fps)
  if t2 is not None:
    if n2 is not None:
      raise TypeError("expected at most one of t2 and n2, but received both")
    else:
      n2 = timecodeToFrame(t2, clip.fps)
  if duration is not None:
    if frameCount is not None:
      raise TypeError("expected at most one of duration and frameCount, but received both")
    else:
      frameCount = timecodeToFrame(duration, clip.fps)

  # Deduce (n1, n2)
  if n1 is not None:
    if n2 is not None:
      if frameCount is not None:
        raise TypeError("expected at most two of n1, n2, frameCount, but received all three")
    else:
      if frameCount is not None:
        n2 = n1 + frameCount
      else:
        n2 = clip.frameCount
  elif n2 is not None:
    if frameCount is not None:
      n1 = n2 - frameCount
    else:
      n1 = 0
  elif frameCount is not None:
    n1 = 0
    n2 = frameCount
  else:
    raise TypeError("insufficient arguments provided")

  # Source: A single VideoClip
  source = (clip,)

  # Metadata: Update the duration
  metadata = copy.copy(clip._metadata)
  metadata.frameCount = n2 - n1

  return SubVideoClip(source, metadata, n1 = n1, n2 = n2)



class SubVideoClip(VideoClip):
  """SubVideoClip(source, metadata, n1, n2)

  Represents a contiguous subsequence [n1, n2) of frames of another video clip.
  """



  def __init__(self, source, metadata, n1, n2):
    super().__init__(source, metadata, isIndirection = True)

    self._n1 = n1
    self._n2 = n2



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__(), (self._n1, self._n2)))



  def __eq__(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super().__eq__(other):
        # The subclip regions must be the same
        if (self._n1, self._n2) == (other._n1, other._n2):
          return True

    return False



  def _framegen(self, n):
    clip = self._source[0]

    n1 = self._n1
    n2 = self._n2

    requestedFrame = n + n1
    if n < 0:
      raise IndexError("received a request for a frame with a negative index ({})".format(n))
    elif n >= n2 - n1:
      raise IndexError("received a request for the frame at index {}, but this subclip only contains {} frames".format(n, n2 - n1))

    image = clip.frame(requestedFrame)

    return image
