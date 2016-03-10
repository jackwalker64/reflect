# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
from ..easing import linear
import copy
import numpy



@clipMethod
def slide(clip, successor, origin, duration = None, frameCount = None, f = None, fValues = None, transitionOnly = False):
  """slide(clip, successor, origin, duration = None, frameCount = None, f = None, fValues = None, transitionOnly = False):

  Returns the concatenation of `clip` and `successor`, but with a "sliding in" transition defined
  by the `origin` ("top" | "bottom" | "left" | "right"), the specified `duration`/`frameCount`,
  and optionally an easing function f : int × float × float × int → float (or a list `fValues` of an
  easing function's output).

  The `transitionOnly` parameter can be set to True to only return the sliding part of the resulting clip.

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
  if f is None and fValues is None:
    # Default to a linear transition
    fValues = [linear(x, 0.0, 1.0, frameCount) for x in range(0, frameCount)]
  elif f is not None:
    if fValues is not None:
      raise TypeError("expected exactly one of f and fValues, but received both")
    fValues = [f(x, 0.0, 1.0, frameCount) for x in range(0, frameCount)]

  if frameCount > clip.frameCount:
    raise ValueError("expected the transition duration to be at most the duration of the input clip, but instead got frameCount = {}, clip.frameCount = {}".format(frameCount, clip.frameCount))
  elif frameCount > successor.frameCount:
    raise ValueError("expected the transition duration to be at most the duration of the input clip, but instead got frameCount = {}, successor.frameCount = {}".format(frameCount, successor.frameCount))

  if frameCount == 0:
    return clip.concat(successor)

  # Generate the transition
  transition = slideTransition(clip, successor, origin, frameCount, fValues)

  if transitionOnly:
    return transition

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
def slideTransition(clip, successor, origin, frameCount, fValues):
  source = (clip.subclip(clip.frameCount - frameCount), successor.subclip(0, frameCount))

  # Push
  from ..clips import transformations
  if "CanonicalOrder" in transformations:
    from reflect.core import vfx

    if isinstance(source[0], vfx.concat.ConcatenatedVideoClip) or isinstance(source[1], vfx.concat.ConcatenatedVideoClip):
      # SlideTransitionVideoClip < ConcatenatedVideoClip
      if isinstance(source[0], vfx.concat.ConcatenatedVideoClip):
        if source[0]._childCount == 0 and source[0]._graph.isLeaf(source[0]): source[0]._graph.removeLeaf(source[0])
        prevSources = list(source[0]._source)
        prevStartFrames = source[0].sourceStartFrames
      else:
        prevSources = [source[0]]
        prevStartFrames = [source[0].frameCount]
      if isinstance(source[1], vfx.concat.ConcatenatedVideoClip):
        if source[1]._childCount == 0 and source[1]._graph.isLeaf(source[1]): source[1]._graph.removeLeaf(source[1])
        nextSources = list(source[1]._source)
        nextStartFrames = source[1].sourceStartFrames
      else:
        nextSources = [source[1]]
        nextStartFrames = [source[1].frameCount]

      i = 0 # prev index
      j = 0 # next index
      n = 0 # Current frame being considered
      finalPartsToConcat = []
      while i < len(prevStartFrames) and j < len(nextStartFrames):
        if prevStartFrames[i] == nextStartFrames[j]:
          # No subclipping is necessary; just construct the slide node
          N = prevStartFrames[i]
          part = prevSources[i].slide(nextSources[j], origin = origin, frameCount = N - n, fValues = fValues[n:N])
          finalPartsToConcat.append(part)
          n = N
          i += 1
          j += 1
        elif prevStartFrames[i] < nextStartFrames[j]:
          # next needs to be split
          N = prevStartFrames[i]
          part = prevSources[i].slide(nextSources[j].subclip(0, N - n), origin = origin, frameCount = N - n, fValues = fValues[n:N])
          finalPartsToConcat.append(part)
          nextSources[j] = nextSources[j].subclip(N - n)
          n = N
          i += 1
        else:
          # prev needs to be split
          N = nextStartFrames[i]
          part = prevSources[i].subclip(0, N - n).slide(nextSources[j], origin = origin, frameCount = N - n, fValues = fValues[n:N])
          finalPartsToConcat.append(part)
          prevSources[i] = prevSources[i].subclip(N - n)
          n = N
          j += 1

      return finalPartsToConcat[0].concat(finalPartsToConcat[1:])

  metadata = copy.copy(clip._metadata)
  metadata.frameCount = frameCount
  return SlideTransitionVideoClip(source, metadata, origin, frameCount, fValues)



class SlideTransitionVideoClip(VideoClip):
  """SlideTransitionVideoClip(source, metadata, origin, frameCount, fValues)

  Represents the transition part of the result of clip.slide(successor, …).
  """



  def __init__(self, source, metadata, origin, frameCount, fValues):
    super().__init__(source, metadata, isIndirection = True)

    self._origin = origin
    self._frameCount = frameCount
    self._fValues = fValues



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__(), self._origin, self._frameCount, tuple(self._fValues)))



  def _pseudoeq(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super()._pseudoeq(other):
        # The slide parameters must be the same.
        # In particular, the effects of the easing functions f should be the same; this is
        # implemented by comparing all possible outputs of the two functions. This is reasonable as
        # long as the duration of this SlideTransitionVideoClip isn't too large.
        if self._origin == other._origin and self._frameCount == other._frameCount and self._fValues == other._fValues:
          return True

    return False



  def __eq__(self, other):
    return self._pseudoeq(other) and self._source == other._source



  def _framegen(self, n):
    clip = self._source[0]
    successor = self._source[1]
    origin = self._origin
    fValues = self._fValues

    progress = fValues[n]

    image = clip.frame(n)

    blittedImage = numpy.copy(image)
    if origin == "top":
      h = int(progress * clip.height)
      w = successor.width
      y = clip.height - h
      imageToBlit = successor.frame(n)[y:clip.height, 0:w]
      blittedImage[0:h, 0:w] = imageToBlit
    elif origin == "bottom":
      h = int(progress * clip.height)
      w = successor.width
      imageToBlit = successor.frame(n)[0:h, 0:w]
      y = clip.height - h
      blittedImage[y:clip.height, 0:clip.width] = imageToBlit
    elif origin == "left":
      h = successor.height
      w = int(progress * clip.width)
      x = clip.width - w
      imageToBlit = successor.frame(n)[0:h, x:clip.width]
      blittedImage[0:h, 0:w] = imageToBlit
    elif origin == "right":
      h = successor.height
      w = int(progress * clip.width)
      imageToBlit = successor.frame(n)[0:h, 0:w]
      x = clip.width - w
      blittedImage[0:h, x:clip.width] = imageToBlit

    return blittedImage
