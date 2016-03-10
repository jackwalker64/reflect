# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import copy



@clipMethod
def brighten(clip, amount):
  """brighten(clip, amount)

  Returns a copy of `clip` where every frame has been brightened/darkened by the specified amount.

  Examples
  --------
  >>> clip.brighten(0.5)    # Brighten by 0.5, making the images brighter
  >>> clip.brighten(0)      # No effect
  >>> clip.brighten(-0.5)   # Darken by 0.5, making the images darker
  >>> clip.brighten(1)      # Guarantee that the resulting frames are entirely white
  >>> clip.brighten(-1)     # Guarantee that the resulting frames are entirely black
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("brighten requires a clip of type VideoClip")

  # Process the arguments
  if not isinstance(amount, int) and not isinstance(amount, float):
    raise TypeError("expected amount to be an int or a float, but instead received a {}".format(type(amount)))
  if amount < -1 or amount > 1:
    raise ValueError("amount must be between -1 and 1 inclusive")

  # Push
  from ..clips import transformations
  if "CanonicalOrder" in transformations:
    from reflect.core import vfx
    if isinstance(clip, vfx.crop.CroppedVideoClip):
      # BrightenedVideoClip > CroppedVideoClip
      pass
    elif isinstance(clip, vfx.resize.ResizedVideoClip):
      if clip.width * clip.height >= clip._source[0].width * clip._source[0].height:
        # BrightenedVideoClip < ResizedVideoClip_↑
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return clip._source[0].brighten(amount).resize(clip.size, interpolation = clip._interpolation)
      else:
        # BrightenedVideoClip > ResizedVideoClip_↓
        pass
    elif isinstance(clip, vfx.brighten.BrightenedVideoClip):
      a = clip._amount
      b = amount
      if b >= 0 and a >= 0:
        # BrightenedVideoClip_↑ = BrightenedVideoClip_↑
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return clip._source[0].brighten(b + a - (a * b))
      elif b <= 0 and a <= 0:
        # BrightenedVideoClip_↓ = BrightenedVideoClip_↓
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return clip._source[0].brighten(b + a + (a * b))
    elif isinstance(clip, vfx.greyscale.GreyscaleVideoClip):
      # BrightenedVideoClip < GreyscaleVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].brighten(amount).greyscale()
    elif isinstance(clip, vfx.blur.BlurredVideoClip):
      # BrightenedVideoClip < BlurredVideoClip
      return clip._source[0].brighten(amount).blur(clip._blurSize)
    elif isinstance(clip, vfx.gaussianBlur.GaussianBlurredVideoClip):
      # BrightenedVideoClip < GaussianBlurredVideoClip
      return clip._source[0].brighten(amount).gaussianBlur(size = clip._blurSize, sigma = clip._sigma)
    elif isinstance(clip, vfx.rate.ChangedRateVideoClip):
      # BrightenedVideoClip < ChangedRateVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].brighten(amount).rate(clip.fps)
    elif isinstance(clip, vfx.reverse.ReversedVideoClip):
      # BrightenedVideoClip < ReversedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].brighten(amount).reverse()
    elif isinstance(clip, vfx.speed.SpedVideoClip):
      # BrightenedVideoClip < SpedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].brighten(amount).speed(clip._scale)
    elif isinstance(clip, vfx.subclip.SubVideoClip):
      # BrightenedVideoClip < SubVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].brighten(amount).subclip(clip._n1, clip._n2)
    elif isinstance(clip, vfx.slide.SlideTransitionVideoClip):
      # BrightenedVideoClip < SlideTransitionVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      a = clip._source[0].brighten(amount)
      b = clip._source[1].brighten(amount)
      return a.slide(b, origin = clip._origin, frameCount = clip._frameCount, fValues = clip._fValues, transitionOnly = True)
    elif isinstance(clip, vfx.composite.CompositeVideoClip):
      # BrightenedVideoClip < CompositeVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      bg = clip._source[0]
      fg = clip._source[1]
      return bg.brighten(amount).composite(fg.brighten(amount), x1 = clip._x1, y1 = clip._y1)
    elif isinstance(clip, vfx.concat.ConcatenatedVideoClip):
      # BrightenedVideoClip < ConcatenatedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return (clip._source[0].brighten(amount)).concat([s.brighten(amount) for s in clip._source[1:]])

  # Source: A single VideoClip
  source = (clip,)

  # Metadata: Exactly the same as the base clip's
  metadata = copy.copy(clip._metadata)

  return BrightenedVideoClip(source, metadata, amount)



class BrightenedVideoClip(VideoClip):
  """BrightenedVideoClip(source, metadata, amount)

  Represents a video clip where every frame has been brightened/darkened by the specified amount.
  """



  def __init__(self, source, metadata, amount):
    super().__init__(source, metadata, isConstant = source[0]._isConstant)

    self._amount = amount



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__(), self._amount))



  def _pseudoeq(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super()._pseudoeq(other):
        # The parameter must be the same
        if self._amount == other._amount:
          return True

    return False



  def __eq__(self, other):
    return self._pseudoeq(other) and self._source == other._source



  def _framegen(self, n):
    amount = self._amount
    image = self._source[0].frame(n)

    if amount >= 0:
      # Brighten
      image = (image * (1 - amount) + (amount * 255)).astype("uint8")
    else:
      # Darken
      image = (image * (1 + amount)).astype("uint8")

    return image
