# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import copy
import numpy
import cv2



@clipMethod
def greyscale(clip):
  """greyscale(clip)

  Returns a copy of `clip` where each pixel is grey with intensity 0.299 R + 0.587 G + 0.114 B.

  Examples
  --------
  >>> clip.greyscale()    # Returns a greyscale version of the clip
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("greyscale requires a clip of type VideoClip")

  # Push
  from ..clips import transformations
  if "CanonicalOrder" in transformations:
    from reflect.core import vfx
    if isinstance(clip, vfx.crop.CroppedVideoClip):
      # GreyscaleVideoClip > CroppedVideoClip
      pass
    elif isinstance(clip, vfx.resize.ResizedVideoClip):
      if clip.width * clip.height >= clip._source[0].width * clip._source[0].height:
        # GreyscaleVideoClip < ResizedVideoClip_↑
        if clip._childCount == 0: clip._graph.removeLeaf(clip)
        return clip._source[0].greyscale().resize(clip.size, interpolation = clip._interpolation)
      else:
        # GreyscaleVideoClip > ResizedVideoClip_↓
        pass
    elif isinstance(clip, vfx.brighten.BrightenedVideoClip):
      # GreyscaleVideoClip > BrightenedVideoClip
      pass
    elif isinstance(clip, vfx.greyscale.GreyscaleVideoClip):
      # GreyscaleVideoClip = GreyscaleVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      return clip._source[0]
    elif isinstance(clip, vfx.blur.BlurredVideoClip):
      # GreyscaleVideoClip < BlurredVideoClip
      return clip._source[0].greyscale().blur(clip._blurSize)
    elif isinstance(clip, vfx.gaussianBlur.GaussianBlurredVideoClip):
      # GreyscaleVideoClip < GaussianBlurredVideoClip
      return clip._source[0].greyscale().gaussianBlur(size = clip._blurSize, sigmaX = clip._sigma[0], sigmaY = clip.sigma[1])
    elif isinstance(clip, vfx.rate.ChangedRateVideoClip):
      # GreyscaleVideoClip < ChangedRateVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      return clip._source[0].greyscale().rate(clip.fps)
    elif isinstance(clip, vfx.reverse.ReversedVideoClip):
      # GreyscaleVideoClip < ReversedVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      return clip._source[0].greyscale().reverse()
    elif isinstance(clip, vfx.speed.SpedVideoClip):
      # GreyscaleVideoClip < SpedVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      return clip._source[0].greyscale().speed(clip._scale)
    elif isinstance(clip, vfx.subclip.SubVideoClip):
      # GreyscaleVideoClip < SubVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      return clip._source[0].greyscale().subclip(clip._n1, clip._n2)
    elif isinstance(clip, vfx.slide.SlideTransitionVideoClip):
      # GreyscaleVideoClip < SlideTransitionVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      a = clip._source[0].greyscale()
      b = clip._source[1].greyscale()
      return a.slide(b, origin = clip._origin, frameCount = clip._frameCount, f = clip._f, transitionOnly = True)
    elif isinstance(clip, vfx.composite.CompositeVideoClip):
      # GreyscaleVideoClip < CompositeVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      bg = clip._source[0]
      fg = clip._source[1]
      return bg.greyscale().composite(fg.greyscale(), x1 = clip._x1, y1 = clip._y1)
    elif isinstance(clip, vfx.concat.ConcatenatedVideoClip):
      # GreyscaleVideoClip < ConcatenatedVideoClip
      if clip._childCount == 0: clip._graph.removeLeaf(clip)
      return (clip._source[0].greyscale()).concat([s.greyscale() for s in clip._source[1:]])

  # Source: A single VideoClip
  source = (clip,)

  # Metadata: Exactly the same as the base clip's
  metadata = copy.copy(clip._metadata)

  return GreyscaleVideoClip(source, metadata)



class GreyscaleVideoClip(VideoClip):
  """GreyscaleVideoClip(source, metadata)

  Represents a video clip where each pixel is grey with intensity 0.299 R + 0.587 G + 0.114 B.
  """



  def __init__(self, source, metadata):
    super().__init__(source, metadata, isConstant = source[0]._isConstant)



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
    image = self._source[0].frame(n)

    grey = numpy.dot(image[:, :, :3], [0.299, 0.587, 0.114]).astype(numpy.uint8)
    w, h = grey.shape
    rgb = numpy.empty((w, h, 3), dtype = numpy.uint8)
    rgb[:, :, 2] = rgb[:, :, 1] = rgb[:, :, 0] = grey

    return rgb
