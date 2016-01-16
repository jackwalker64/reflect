# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
from ..util import timecodeToFrame
import copy



@clipMethod
def composite(clip, fg, x1 = None, y1 = None, t1 = None, x2 = None, y2 = None, xc = None, yc = None, t2 = None, n1 = None, n2 = None):
  """composite(clip, fg, x1 = None, y1 = None, t1 = None, x2 = None, y2 = None, xc = None, yc = None, t2 = None, n1 = None, n2 = None)

  Returns `clip` with the `fg` clip overlaid on top of it.

  `t1` and `t2` specify the start and end timecodes to place the `fg` clip at.
  Alternatively use `n1` and `n2` to specify the start and end frames.

  Examples
  --------
  >>> clip.composite(clip2, xc = clip.width / 2, yc = clip.height / 2) # overlays `clip2` centred about `clip`'s centre
  >>> clip.composite(clip2, t1 = "1:00")                               # overlays `clip2` at (0, 0) starting one minute after `clip`'s beginning
  >>> clip.composite(clip2, t2 = clip.duration)                        # overlays `clip2` at the end of `clip`
  >>> clip.composite(clip2, n1 = clip.frameCount / 2)                  # overlays `clip2` starting halfway through `clip`
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("composite requires a clip of type VideoClip")

  # Deduce (n1, n2)
  if n1 is not None:
    if t1 is not None:
      raise TypeError("expected at most one of n1 and t1, but received both")
    if n2 is not None:
      if t2 is not None:
        raise TypeError("expected at most one of n2 and t2, but received both")
    else:
      # Deduce n2 from n1
      n2 = n1 + fg.frameCount
  elif n2 is not None:
    if t2 is not None:
      raise TypeError("expected at most one of n2 and t2, but received both")
    else:
      # Deduce n1 from n2
      n1 = n2 - fg.frameCount
  elif t1 is not None or t2 is not None:
    # Deduce (n1, n2) from t1 and/or t2
    if t1 is not None:
      n1 = timecodeToFrame(t1, fps = clip.fps)
    if t2 is not None:
      n2 = timecodeToFrame(t2, fps = clip.fps)
    if n2 is None:
      n2 = n1 + fg.frameCount
    if n1 is None:
      n1 = n2 - fg.frameCount
  else:
    # Default to placing the foreground clip at the beginning of the base clip
    n1 = 0
    n2 = fg.frameCount

  # Deduce x1
  if x1 is not None:
    # Check that the other arguments don't contradict x1
    if x2 is not None and int(x1 + fg.width) != int(x2):
      raise ValueError("inconsistent arguments: x1 = {}, x2 = {} (the foreground clip's width is {})".format(x1, x2, fg.width))
    if xc is not None and int(x1 + fg.width) != int(xc * 2):
      raise ValueError("inconsistent arguments: x1 = {}, xc = {} (the foreground clip's width is {})".format(x1, xc, fg.width))
  else:
    if x2 is not None:
      x1 = x2 - fg.width
    elif xc is not None:
      x1 = xc - fg.width / 2
    else:
      x1 = 0

  # Deduce y1
  if y1 is not None:
    # Check that the other arguments don't contradict y1
    if y2 is not None and int(y1 + fg.height) != int(y2):
      raise ValueError("inconsistent arguments: y1 = {}, y2 = {} (the foreground clip's height is {})".format(y1, y2, fg.height))
    if yc is not None and int(y1 + fg.height) != int(yc * 2):
      raise ValueError("inconsistent arguments: y1 = {}, yc = {} (the foreground clip's height is {})".format(y1, yc, fg.width))
  else:
    if y2 is not None:
      y1 = y2 - fg.height
    elif yc is not None:
      y1 = yc - fg.height / 2
    else:
      y1 = 0

  n1 = int(n1)
  n2 = int(n2)
  x1 = int(x1)
  y1 = int(y1)

  # Sources: The base clip, and the foreground clip
  source = (clip, fg)

  # Metadata: Exactly the same as the base clip's
  metadata = copy.copy(clip._metadata)

  return CompositeVideoClip(source, metadata, n1 = n1, n2 = n2, x1 = x1, y1 = y1)



class CompositeVideoClip(VideoClip):
  """CompositeVideoClip(source, metadata, n1, n2, x1, y1)

  Represents a video clip that has had another clip overlaid in the foreground.
  """



  def __init__(self, source, metadata, n1, n2, x1, y1):
    super().__init__(source, metadata)

    self._n1 = n1
    self._n2 = n2
    self._x1 = x1
    self._y1 = y1



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__(), (self._n1, self._n2, self._x1, self._y1)))



  def __eq__(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super().__eq__(other):
        # The crop regions must be the same
        if (self._n1, self._n2, self._x1, self._y1) == (other._n1, other._n2, other._x1, other._y1):
          return True

    return False



  def _framegen(self, n):
    clip = self._source[0]
    fg = self._source[1]

    n1 = self._n1
    n2 = self._n2
    x1 = self._x1
    y1 = self._y1
    x2 = x1 + fg.width
    y2 = y1 + fg.height

    image = clip.frame(n)

    if n < n1 or n >= n2:
      # The foreground clip is not being shown at frame n
      return image

    if x2 < 0 or x1 > clip.width or y2 < 0 or y1 > clip.height:
      # The foreground clip is not currently visible
      return image

    # Determine the region of the foreground frame that will actually be visible when blitted
    fgx1 = max(0, -x1)
    fgx2 = min(fg.width, fg.width - (x2 - clip.width))
    fgy1 = max(0, -y1)
    fgy2 = min(fg.height, fg.height - (y2 - clip.height))
    imageToBlit = fg.frame(n - n1)[fgy1:fgy2, fgx1:fgx2]

    # Blit the foreground frame over the background frame
    x1 = max(0, x1)
    x2 = x1 + (fgx2 - fgx1)
    y1 = max(0, y1)
    y2 = y1 + (fgy2 - fgy1)
    image[y1:y2, x1:x2] = imageToBlit

    return image
