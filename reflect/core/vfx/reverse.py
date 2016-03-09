# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import copy



@clipMethod
def reverse(clip):
  """reverse(clip)

  Returns `clip` with its frames in the reverse order.

  Examples
  --------
  >>> clip.reverse()   # frame 0 becomes frame (clip.frameCount - 1) etc
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("expected a clip of type VideoClip")

  # Push
  from ..clips import transformations
  if "CanonicalOrder" in transformations:
    from reflect.core import vfx
    if isinstance(clip, vfx.crop.CroppedVideoClip):
      # ReversedVideoClip > CroppedVideoClip
      pass
    elif isinstance(clip, vfx.resize.ResizedVideoClip):
      if clip.width * clip.height >= clip._source[0].width * clip._source[0].height:
        # ReversedVideoClip < ResizedVideoClip_↑
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return clip._source[0].reverse().resize(clip.size, interpolation = clip._interpolation)
      else:
        # ReversedVideoClip > ResizedVideoClip_↓
        pass
    elif isinstance(clip, vfx.brighten.BrightenedVideoClip):
      # ReversedVideoClip > BrightenedVideoClip
      pass
    elif isinstance(clip, vfx.greyscale.GreyscaleVideoClip):
      # ReversedVideoClip > GreyscaleVideoClip
      pass
    elif isinstance(clip, vfx.blur.BlurredVideoClip):
      # ReversedVideoClip > BlurredVideoClip
      pass
    elif isinstance(clip, vfx.gaussianBlur.GaussianBlurredVideoClip):
      # ReversedVideoClip > GaussianBlurredVideoClip
      pass
    elif isinstance(clip, vfx.rate.ChangedRateVideoClip):
      # ReversedVideoClip > ChangedRateVideoClip
      pass
    elif isinstance(clip, vfx.reverse.ReversedVideoClip):
      # ReversedVideoClip = ReversedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0]
    elif isinstance(clip, vfx.speed.SpedVideoClip):
      # ReversedVideoClip < SpedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].reverse().speed(clip._scale)
    elif isinstance(clip, vfx.subclip.SubVideoClip):
      # ReversedVideoClip < SubVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].reverse().subclip(clip.frameCount - clip._n2, clip.frameCount - clip._n1)
    elif isinstance(clip, vfx.slide.SlideTransitionVideoClip):
      # ReversedVideoClip < SlideTransitionVideoClip
      # if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      # a = clip._source[0].reverse()
      # b = clip._source[1].reverse()
      # return a.slide(b, origin = clip._origin, frameCount = clip._frameCount, f = clip._f, transitionOnly = True)
      raise NotImplementedError()
    elif isinstance(clip, vfx.composite.CompositeVideoClip):
      # ReversedVideoClip < CompositeVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      bg = clip._source[0]
      fg = clip._source[1]
      return bg.reverse().composite(fg.reverse(), x1 = clip._x1, y1 = clip._y1)
    elif isinstance(clip, vfx.concat.ConcatenatedVideoClip):
      # ReversedVideoClip < ConcatenatedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      n = len(clip._source)
      return (clip._source[n-1].reverse()).concat([s.reverse() for s in reversed(clip._source[0:n-1])])

  source = (clip,)
  metadata = copy.copy(clip._metadata)

  return ReversedVideoClip(source, metadata)



class ReversedVideoClip(VideoClip):
  """ReversedVideoClip(source, metadata, n1, n2)

  Represents a clip with its frames in the reverse order.
  """



  def __init__(self, source, metadata):
    super().__init__(source, metadata, isIndirection = True, isConstant = source[0]._isConstant)



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__()))



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
    clip = self._source[0]

    image = clip.frame(clip.frameCount - n - 1)

    return image
