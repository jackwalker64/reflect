# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import copy
import collections
from itertools import accumulate
from bisect import bisect_left



@clipMethod
def concat(clip, *others):
  """concat(clip, *others)

  Returns a VideoClip containing the frames of `clip` immediately followed by the frames in one or
  more other VideoClips (`*others`).

  Examples
  --------
  >>> clip.concat(clip2)          # `clip` immediately followed by `clip2`
  >>> clip.concat(clip2, clip3)   # Equivalent to clip.concat(clip2).concat(clip3)
  >>> clip.concat([clip2, clip3]) # Equivalent to clip.concat(clip2).concat(clip3)
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("expected a clip of type VideoClip")

  if len(others) == 1 and isinstance(others[0], collections.Iterable):
    # The call was something like clip1.concat([clip2, clip3]) instead of clip1.concat(clip2, clip3)
    others = others[0]

  if len(others) < 1:
    raise TypeError("expected at least two clips to concatenate together")

  others = [(other.resize(size = clip.size) if other.size != clip.size else other) for other in others]

  # Sources
  source = (clip,) + tuple(others)

  # Metadata: Update the duration
  metadata = copy.copy(clip._metadata)
  metadata.frameCount = sum(c.frameCount for c in source)

  return ConcatenatedVideoClip(source, metadata)



class ConcatenatedVideoClip(VideoClip):
  """ConcatenatedVideoClip(source, metadata)

  Represents a sequence of two or more video clips.
  """



  def __init__(self, source, metadata, sourcesAreFlat = True):
    super().__init__(source, metadata, isIndirection = True, isConstant = False)

    self._sourceStartFrames = None # Initialised only when it's needed
    self._mostRecentSourceIndex = 0 # Remembers the previously accessed source clip



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
    image = None

    if self._mostRecentSourceIndex == 0 and n < self.sourceStartFrames[0]:
      # We are still accessing the most recent clip
      clipIndex = self._mostRecentSourceIndex
    elif n >= self.sourceStartFrames[self._mostRecentSourceIndex - 1] and n < self.sourceStartFrames[self._mostRecentSourceIndex]:
      # We are still accessing the most recent clip
      clipIndex = self._mostRecentSourceIndex
    elif n >= self.sourceStartFrames[self._mostRecentSourceIndex] and n < self.sourceStartFrames[self._mostRecentSourceIndex + 1]:
      # We are now accessing the clip that comes after the most recently accessed clip
      clipIndex = self._mostRecentSourceIndex + 1
    elif n == 0:
      # We have returned to the start of the clip
      clipIndex = 0
    else:
      # Otherwise do a binary search
      clipIndex = bisect_left(self.sourceStartFrames, n + 1)

    self._mostRecentSourceIndex = clipIndex

    if clipIndex == 0:
      offset = 0
    elif clipIndex < len(self._source):
      offset = self.sourceStartFrames[clipIndex - 1]
    else:
      raise IndexError("received a request for the frame at index {}, but this sequence of video clips contains only {} frames".format(n, self.frameCount))

    clip = self._source[clipIndex]
    image = clip.frame(n - offset)

    return image



  @property
  def sourceStartFrames(self):
    if self._sourceStartFrames is None:
      self._sourceStartFrames = list(accumulate([clip.frameCount for clip in self._source]))
    return self._sourceStartFrames
