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

  # Push
  from ..clips import transformations
  if "CanonicalOrder" in transformations:
    from reflect.core import vfx
    if isinstance(clip, vfx.crop.CroppedVideoClip):
      # SpedVideoClip > CroppedVideoClip
      pass
    elif isinstance(clip, vfx.resize.ResizedVideoClip):
      if clip.width * clip.height >= clip._source[0].width * clip._source[0].height:
        # SpedVideoClip < ResizedVideoClip_↑
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return clip._source[0].speed(scale).resize(clip.size, interpolation = clip._interpolation)
      else:
        # SpedVideoClip > ResizedVideoClip_↓
        pass
    elif isinstance(clip, vfx.brighten.BrightenedVideoClip):
      # SpedVideoClip > BrightenedVideoClip
      pass
    elif isinstance(clip, vfx.greyscale.GreyscaleVideoClip):
      # SpedVideoClip > GreyscaleVideoClip
      pass
    elif isinstance(clip, vfx.blur.BlurredVideoClip):
      # SpedVideoClip > BlurredVideoClip
      pass
    elif isinstance(clip, vfx.gaussianBlur.GaussianBlurredVideoClip):
      # SpedVideoClip > GaussianBlurredVideoClip
      pass
    elif isinstance(clip, vfx.rate.ChangedRateVideoClip):
      # SpedVideoClip > ChangedRateVideoClip
      pass
    elif isinstance(clip, vfx.reverse.ReversedVideoClip):
      # SpedVideoClip > ReversedVideoClip
      pass
    elif isinstance(clip, vfx.speed.SpedVideoClip):
      # SpedVideoClip = SpedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].speed(scale)
    elif isinstance(clip, vfx.subclip.SubVideoClip):
      # SpedVideoClip < SubVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].speed(scale).subclip(int(clip._n1 / scale), int(clip._n2 / scale))
    elif isinstance(clip, vfx.slide.SlideTransitionVideoClip):
      # SpedVideoClip < SlideTransitionVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      a = clip._source[0].speed(scale)
      b = clip._source[1].speed(scale)
      return a.slide(b, origin = clip._origin, frameCount = int(clip._frameCount / scale), f = clip._f, transitionOnly = True)
    elif isinstance(clip, vfx.composite.CompositeVideoClip):
      # SpedVideoClip < CompositeVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      bg = clip._source[0].speed(scale)
      fg = clip._source[1].speed(scale)
      return bg.composite(fg, x1 = clip._x1, y1 = clip._y1)
    elif isinstance(clip, vfx.concat.ConcatenatedVideoClip):
      # SpedVideoClip < ConcatenatedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return (clip._source[0].speed(scale)).concat([s.speed(scale) for s in clip._source[1:]])

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
    super().__init__(source, metadata, isIndirection = True, isConstant = source[0]._isConstant)

    self._scale = scale



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__(), self._scale))



  def _pseudoeq(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super()._pseudoeq(other):
        # The scale factors must be the same
        if self._scale == other._scale:
          return True

    return False



  def __eq__(self, other):
    return self._pseudoeq(other) and self._source == other._source



  def _framegen(self, n):
    return self._source[0].frame(int(n * self._scale))
