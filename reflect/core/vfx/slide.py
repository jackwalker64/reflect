# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
from ..easing import linear
import copy
import numpy



@clipMethod
def slide(clip, successor, origin, duration = None, frameCount = None, f = None):
  """slide(clip, successor, origin, duration = None, frameCount = None, f = None):

  Returns the concatenation of `clip` and `successor`, but with a "sliding in" transition defined
  by the `origin` ("top" | "bottom" | "left" | "right"), the specified `duration`/`frameCount`,
  and optionally an easing function f : int × int → float.

  Examples
  --------
  >>> clip.slide(c, "right", frameCount = 20)                    # make `c` slide in from the right over 20 frames
  >>> clip.slide(c, "top", 5, f = reflect.core.easing.inOutQuad) # use a builtin easing function to make `c` slide in from the top over 5 seconds
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("slide requires a clip of type VideoClip")

  # Process the arguments
  if not isinstance(successor, VideoClip):
    raise TypeError("expected successor to be of type VideoClip, but instead received a {}".format(type(successor)))
  if clip.fps != successor.fps:
    raise ValueError("expected clip and successor to have equal fps, but instead found clip.fps = {} and successor.fps = {}".format(clip.fps, successor.fps))
  if clip.size != successor.size:
    raise ValueError("expected clip and successor to have equal size, but instead found clip.size = {} and successor.size = {}".format(clip.size, successor.size))
  if origin not in ["top", "bottom", "left", "right"]:
    raise ValueError("expected origin to be in [\"top\", \"bottom\", \"left\", \"right\"], but instead received {}".format(origin))
  if duration is not None:
    if frameCount is not None:
      raise TypeError("expected exactly one of duration and frameCount, but received both")
    frameCount = int(duration * clip.fps)
  if f is None:
    f = linear # Default to a linear transition

  if frameCount > clip.frameCount:
    raise ValueError("expected the transition duration to be at most the duration of the input clip, but instead got frameCount = {}, clip.frameCount = {}".format(frameCount, successor.frameCount))
  elif frameCount > successor.frameCount:
    raise ValueError("expected the transition duration to be at most the duration of the input clip, but instead got frameCount = {}, successor.frameCount = {}".format(frameCount, clip.frameCount))

  if frameCount == 0:
    return clip.concat(successor)

  # Generate the transition
  transition = slideTransition(clip, successor, origin, frameCount, f)

  if frameCount == clip.frameCount:
    if frameCount == successor.frameCount:
      return transition
    else:
      return transition.concat(successor.subclip(frameCount))
  elif frameCount == successor.frameCount:
    return clip.subclip(0, -frameCount).concat(transition)
  else:
    return clip.subclip(0, -frameCount).concat(transition, successor.subclip(frameCount))



@clipMethod
def slideTransition(clip, successor, origin, frameCount, f):
  source = (clip, successor)
  metadata = copy.copy(clip._metadata)
  metadata.frameCount = frameCount
  return SlideTransitionVideoClip(source, metadata, origin, frameCount, f)



class SlideTransitionVideoClip(VideoClip):
  """SlideTransitionVideoClip(source, metadata, origin, frameCount, f)

  Represents the transition part of the result of clip.slide(successor, …).
  """



  def __init__(self, source, metadata, origin, frameCount, f):
    super().__init__(source, metadata, isIndirection = True)

    self._origin = origin
    self._frameCount = frameCount
    self._f = f



  @memoizeHash
  def __hash__(self):
    import inspect
    return hash((super().__hash__(), self._origin, self._frameCount, inspect.getsource(self._f)))



  def _pseudoeq(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super()._pseudoeq(other):
        # The slide parameters must be the same
        import inspect
        if self._origin == other._origin and self._frameCount == other._frameCount and inspect.getsource(self._f) == inspect.getsource(other._f):
          return True

    return False



  def __eq__(self, other):
    return self._pseudoeq(other) and self._source == other._source



  def _framegen(self, n):
    clip = self._source[0]
    successor = self._source[1]
    origin = self._origin
    frameCount = self._frameCount
    f = self._f

    progress = f(n, 0.0, 1.0, frameCount)

    image = clip.frame(clip.frameCount - frameCount + n)

    if origin == "right":
      h = successor.height
      w = int(progress * clip.width)
      imageToBlit = successor.frame(n)[0:h, 0:w]
      x = clip.width - w
      blittedImage = numpy.copy(image)
      blittedImage[0:h, x:clip.width] = imageToBlit

    return blittedImage
