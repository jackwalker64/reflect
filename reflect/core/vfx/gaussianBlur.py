# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import cv2
import copy



@clipMethod
def gaussianBlur(clip, size = None, width = None, height = None, sigma = (0, 0)):
  """gaussianBlur(clip, size = None, width = None, height = None, sigma = (0, 0))

  Returns a copy of `clip` where every frame has been blurred by the specified size.

  Examples
  --------
  >>> clip.gaussianBlur(5)                         # gaussian blur by 5
  >>> clip.gaussianBlur(width = 5)                 # gaussian blur by 5 only in the horizontal direction
  >>> clip.gaussianBlur((10, 5))                   # gaussian blur by 10 horizontally, and 5 vertically
  >>> clip.gaussianBlur(width = 10, height = 5))   # gaussian blur by 10 horizontally, and 5 vertically
  >>> clip.gaussianBlur(5, sigma = (2, 2))         # gaussian blur by 5, explicitly setting the sigma values
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("gaussianBlur requires a clip of type VideoClip")

  # Process the arguments
  if size is not None:
    if width is not None or height is not None:
      raise TypeError("either specify size, or specify at least one of width and height")
    elif isinstance(size, int):
      (width, height) = (size, size)
    elif isinstance(size, tuple):
      (width, height) = size
    else:
      raise TypeError("size must be either an int or a (width, height) pair")
  else:
    if width is not None and height is not None:
      pass
    elif width is not None and height is None:
      height = 1
    elif width is None and height is not None:
      width = 1
    else:
      raise TypeError("either size, width, or height must be provided")

  if not isinstance(width, int) or not isinstance(height, int) or width < 1 or height < 1 or width % 2 == 0 or height % 2 == 0:
    raise ValueError("gaussian blur amounts must be odd integers greater than or equal to 1")

  # Push
  from ..clips import transformations
  if "CanonicalOrder" in transformations:
    from reflect.core import vfx
    blurSize = (width, height)
    if isinstance(clip, vfx.crop.CroppedVideoClip):
      # GaussianBlurredVideoClip > CroppedVideoClip
      pass
    elif isinstance(clip, vfx.resize.ResizedVideoClip):
      # GaussianBlurredVideoClip > ResizedVideoClip_↓
      # GaussianBlurredVideoClip | ResizedVideoClip_↑
      pass
    elif isinstance(clip, vfx.brighten.BrightenedVideoClip):
      # GaussianBlurredVideoClip > BrightenedVideoClip
      pass
    elif isinstance(clip, vfx.greyscale.GreyscaleVideoClip):
      # GaussianBlurredVideoClip > GreyscaleVideoClip
      pass
    elif isinstance(clip, vfx.blur.BlurredVideoClip):
      # GaussianBlurredVideoClip | BlurredVideoClip
      pass
    elif isinstance(clip, vfx.gaussianBlur.GaussianBlurredVideoClip):
      # GaussianBlurredVideoClip | GaussianBlurredVideoClip
      pass
    elif isinstance(clip, vfx.rate.ChangedRateVideoClip):
      # GaussianBlurredVideoClip < ChangedRateVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].gaussianBlur(blurSize, sigma = sigma).rate(clip.fps)
    elif isinstance(clip, vfx.reverse.ReversedVideoClip):
      # GaussianBlurredVideoClip < ReversedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].gaussianBlur(blurSize, sigma = sigma).reverse()
    elif isinstance(clip, vfx.speed.SpedVideoClip):
      # GaussianBlurredVideoClip < SpedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].gaussianBlur(blurSize, sigma = sigma).speed(clip._scale)
    elif isinstance(clip, vfx.subclip.SubVideoClip):
      # GaussianBlurredVideoClip < SubVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].gaussianBlur(blurSize, sigma = sigma).subclip(clip._n1, clip._n2)
    elif isinstance(clip, vfx.slide.SlideTransitionVideoClip):
      # GaussianBlurredVideoClip | SlideTransitionVideoClip
      pass
    elif isinstance(clip, vfx.composite.CompositeVideoClip):
      # GaussianBlurredVideoClip | CompositeVideoClip
      pass
    elif isinstance(clip, vfx.concat.ConcatenatedVideoClip):
      # GaussianBlurredVideoClip < ConcatenatedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return (clip._source[0].gaussianBlur(blurSize, sigma = sigma)).concat([s.gaussianBlur(blurSize, sigma = sigma) for s in clip._source[1:]])

  # Source: A single VideoClip to be gaussian blurred
  source = (clip,)

  # Metadata: Exactly the same as the base clip's
  metadata = copy.copy(clip._metadata)

  return GaussianBlurredVideoClip(source, metadata, (width, height), sigma)



class GaussianBlurredVideoClip(VideoClip):
  """GaussianBlurredVideoClip(source, metadata, size, sigma)

  Represents a video clip that has had each of its frames gaussian blurred.
  """



  def __init__(self, source, metadata, size, sigma):
    super().__init__(source, metadata, isConstant = source[0]._isConstant)

    self._blurSize = size
    self._sigma = sigma



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__(), self._blurSize, self._sigma))



  def _pseudoeq(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super()._pseudoeq(other):
        # The gaussian blur parameters must be the same
        if self._blurSize == other._blurSize and self._sigma == other._sigma:
          return True

    return False



  def __eq__(self, other):
    return self._pseudoeq(other) and self._source == other._source



  def _framegen(self, n):
    image = self._source[0].frame(n)
    return cv2.GaussianBlur(image, self._blurSize, self._sigma[0], self._sigma[1])
