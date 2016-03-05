# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import copy



@clipMethod
def rate(clip, fps = None, delay = None):
  """rate(clip, fps = None, delay = None)

  Returns a copy of `clip` with a different fps value.

  Either specify the new number of frames per second with `fps`, or specify a `delay` (number of
  seconds per frame) to compute `fps` automatically.

  Examples
  --------
  >>> clip.rate(30)           # Sets the fps to 30
  >>> clip.rate(delay = 0.04) # Each frame will last for 0.04 seconds, i.e. the new fps value is 25
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("expected a clip of type VideoClip")

  if delay is not None:
    if fps is not None:
      raise TypeError("only one of either fps or delay should be specified")
    fps = 1.0 / delay

  if fps is None:
    raise TypeError("expected one of fps or delay to be specified")

  # Push
  from ..clips import transformations
  if "CanonicalOrder" in transformations:
    from reflect.core import vfx
    if isinstance(clip, vfx.crop.CroppedVideoClip):
      # ChangedRateVideoClip > CroppedVideoClip
      pass
    elif isinstance(clip, vfx.resize.ResizedVideoClip):
      if clip.width * clip.height >= clip._source[0].width * clip._source[0].height:
        # ChangedRateVideoClip < ResizedVideoClip_↑
        if clip._childCount == 0: clip._graph.removeLeaf(clip)
        return clip._source[0].rate(fps).resize(clip.size, clip._interpolation)
      else:
        # ChangedRateVideoClip > ResizedVideoClip_↓
        pass
    elif isinstance(clip, vfx.brighten.BrightenedVideoClip):
      # ChangedRateVideoClip > BrightenedVideoClip
      pass
    elif isinstance(clip, vfx.greyscale.GreyscaleVideoClip):
      # ChangedRateVideoClip > GreyscaleVideoClip
      pass
    elif isinstance(clip, vfx.blur.BlurredVideoClip):
      # ChangedRateVideoClip > BlurredVideoClip
      pass
    elif isinstance(clip, vfx.gaussianBlur.GaussianBlurredVideoClip):
      # ChangedRateVideoClip > GaussianBlurredVideoClip
      pass
    elif isinstance(clip, vfx.rate.ChangedRateVideoClip):
      # ChangedRateVideoClip = ChangedRateVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      return clip._source[0].rate(fps)
    elif isinstance(clip, vfx.reverse.ReversedVideoClip):
      # ChangedRateVideoClip < ReversedVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      return clip._source[0].rate(fps).reverse()
    elif isinstance(clip, vfx.speed.SpedVideoClip):
      # ChangedRateVideoClip < SpedVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      return clip._source[0].rate(fps).speed(clip._scale)
    elif isinstance(clip, vfx.subclip.SubVideoClip):
      # ChangedRateVideoClip < SubVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      return clip._source[0].rate(fps).subclip(clip._n1, clip._n2)
    elif isinstance(clip, vfx.slide.SlideTransitionVideoClip):
      # ChangedRateVideoClip < SlideTransitionVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      a = clip._source[0].rate(fps)
      b = clip._source[1].rate(fps)
      return a.slide(b, origin = clip._origin, frameCount = clip._frameCount, f = clip._f, transitionOnly = True)
    elif isinstance(clip, vfx.composite.CompositeVideoClip):
      # ChangedRateVideoClip < CompositeVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      bg = clip._source[0]
      fg = clip._source[1]
      return bg.rate(fps).composite(fg.rate(fps), x1 = clip._x1, y1 = clip._y1)
    elif isinstance(clip, vfx.concat.ConcatenatedVideoClip):
      # ChangedRateVideoClip < ConcatenatedVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      return (clip._source[0].rate(fps)).concat([s.rate(fps) for s in clip._source[1:]])

  # Source: A single VideoClip
  source = (clip,)

  # Metadata: Update the total number of frames and the fps
  metadata = copy.copy(clip._metadata)
  metadata.fps = float(fps)

  return ChangedRateVideoClip(source, metadata)



class ChangedRateVideoClip(VideoClip):
  """ChangedRateVideoClip(source, metadata)

  Represents a video clip whose fps property has been changed.
  """



  def __init__(self, source, metadata):
    super().__init__(source, metadata, isIndirection = True, isConstant = source[0]._isConstant)



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
    return self._source[0].frame(n)
