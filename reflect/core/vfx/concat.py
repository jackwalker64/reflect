# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import copy
import collections



@clipMethod
def concat(clip, *others, autoResize = True):
  """concat(clip, *others, autoResize = True)

  Returns a VideoClip containing the frames of `clip` immediately followed by the frames in one or
  more other VideoClips (`*others`).

  If autoResize is True, clips in `others` will be scaled to have the same dimensions as `clip`.
  If autoResize is False, clips in `others` will just be placed at (0, 0) and will retain their
  original dimensions.

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

  if autoResize:
    othersTuple = tuple([(other.resize(size = clip.size) if other.size != clip.size else other) for other in others])
  else:
    # TODO: Resize the canvas of each clip to the same dimensions, placing each clip at (0, 0) and making any empty space transparent
    # (Currently this just passes the clips through at their original dimensions, which means concatenated.frame(n) isn't necessarily constant)
    othersTuple = tuple(others)

  # Source: The first VideoClip, and at least one other
  source = (clip,) + othersTuple

  # Metadata: Update the duration
  metadata = copy.copy(clip._metadata)
  metadata.frameCount = sum(c.frameCount for c in source)

  return ConcatenatedVideoClip(source, metadata)



class ConcatenatedVideoClip(VideoClip):
  """ConcatenatedVideoClip(source, metadata)

  Represents a sequence of two or more video clips.
  """



  def __init__(self, source, metadata):
    super().__init__(source, metadata, isIndirection = True)



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
    image = None

    i = 0
    for clip in self._source:
      if n < i + clip.frameCount:
        image = clip.frame(n - i)
        break
      else:
        i += clip.frameCount

    if image is None:
      raise IndexError("received a request for the frame at index {}, but this sequence of video clips contains only {} frames".format(n, self.frameCount))

    return image
