# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import cv2
import copy



@clipMethod
def resize(clip, size = None, width = None, height = None, interpolation = cv2.INTER_AREA):
  """resize(clip, size = None, width = None, height = None, interpolation = cv2.INTER_AREA)

  Returns a copy of `clip` with the new frame dimensions.

  Examples
  --------
  >>> clip.resize((1280, 720))                 # 1280×720
  >>> clip.resize(0.5)                         # (0.5*oldWidth)×(0.5*oldHeight)
  >>> clip.resize(width = 1280)                # 1280×? where ? is computed automatically to preserve aspect ratio
  >>> clip.resize(height = 720)                # ?×720 where ? is computed automatically to preserve aspect ratio
  >>> clip.resize(width = 1280, height = 1024) # 1280×1024
  >>> clip.resize(0.5, cv2.INTER_NEAREST)      # (0.5*oldWidth)×(0.5*oldHeight) with nearest-neighbour interpolation
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("resize requires a clip of type VideoClip")

  # Process the arguments
  (oldWidth, oldHeight) = clip.size
  if size is not None:
    if width is not None or height is not None:
      raise TypeError("either specify size, or specify at least one of width and height")
    elif isinstance(size, int) or isinstance(size, float):
      (width, height) = (round(oldWidth * size), round(oldHeight * size))
    elif isinstance(size, tuple):
      (width, height) = size
    else:
      raise TypeError("size must be either an int, a float, or a (width, height) pair")
  else:
    if width is not None and height is not None:
      pass
    elif width is not None and height is None:
      height = round(width / oldWidth * oldHeight)
    elif width is None and height is not None:
      width = round(height / oldHeight * oldWidth)
    else:
      raise TypeError("resize requires either size, width, or height to be provided")
  (width, height) = (round(width), round(height))

  if (width, height) == clip.size:
    # There is no resizing to be done, so just return the source clip
    return clip

  if width == 0:
    raise ValueError("attempted to resize a clip to have zero width")
  if height == 0:
    raise ValueError("attempted to resize a clip to have zero height")

  # Push
  from ..clips import transformations
  if "CanonicalOrder" in transformations:
    from reflect.core import vfx
    size = (width, height)
    if width * height >= clip.width * clip.height:
      if isinstance(clip, vfx.resize.ResizedVideoClip):
        if clip.width * clip.height >= clip._source[0].width * clip._source[0].height and clip._interpolation == interpolation:
          # ResizedVideoClip_↑ = ResizedVideoClip_↑
          if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
          return clip._source[0].resize(size, interpolation = interpolation)
      elif isinstance(clip, vfx.concat.ConcatenatedVideoClip):
        # ResizedVideoClip_↑ < ConcatenatedVideoClip
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return (clip._source[0].resize(size, interpolation = interpolation)).concat([s.resize(size, interpolation = interpolation) for s in clip._source[1:]])
    else:
      if isinstance(clip, vfx.resize.ResizedVideoClip):
        if clip._interpolation == interpolation:
          # ResizedVideoClip_↓ = ResizedVideoClip_↓
          # ResizedVideoClip_↓ = ResizedVideoClip_↑
          if clip._source[0].size == size:
            # Annihilate
            if clip._childCount == 0 and clip._graph.isLeaf(clip):
              clip._graph.removeLeaf(clip)
              clip._source[0]._childCount -= 1
              if clip._source[0]._childCount == 0:
                clip._source[0]._graph.addLeaf(clip._source[0])
            return clip._source[0]
          else:
            if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
            return clip._source[0].resize(size, interpolation = interpolation)
      elif isinstance(clip, vfx.brighten.BrightenedVideoClip):
        # ResizedVideoClip_↓ < BrightenedVideoClip
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return clip._source[0].resize(size, interpolation = interpolation).brighten(clip._amount)
      elif isinstance(clip, vfx.greyscale.GreyscaleVideoClip):
        # ResizedVideoClip_↓ < GreyscaleVideoClip
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return clip._source[0].resize(size, interpolation = interpolation).greyscale()
      elif isinstance(clip, vfx.blur.BlurredVideoClip):
        # ResizedVideoClip_↓ < BlurredVideoClip
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return clip._source[0].resize(size, interpolation = interpolation).blur(clip._blurSize)
      elif isinstance(clip, vfx.gaussianBlur.GaussianBlurredVideoClip):
        # ResizedVideoClip_↓ < GaussianBlurredVideoClip
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return clip._source[0].resize(size, interpolation = interpolation).gaussianBlur(size = clip._blurSize, sigma = clip._sigma)
      elif isinstance(clip, vfx.rate.ChangedRateVideoClip):
        # ResizedVideoClip_↓ < ChangedRateVideoClip
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return clip._source[0].resize(size, interpolation = interpolation).rate(clip.fps)
      elif isinstance(clip, vfx.reverse.ReversedVideoClip):
        # ResizedVideoClip_↓ < ReversedVideoClip
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return clip._source[0].resize(size, interpolation = interpolation).reverse()
      elif isinstance(clip, vfx.speed.SpedVideoClip):
        # ResizedVideoClip_↓ < SpedVideoClip
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return clip._source[0].resize(size, interpolation = interpolation).speed(clip._scale)
      elif isinstance(clip, vfx.subclip.SubVideoClip):
        # ResizedVideoClip_↓ < SubVideoClip
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return clip._source[0].resize(size, interpolation = interpolation).subclip(clip._n1, clip._n2)
      elif isinstance(clip, vfx.slide.SlideTransitionVideoClip):
        # ResizedVideoClip_↓ < SlideTransitionVideoClip
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        a = clip._source[0].resize(size, interpolation = interpolation)
        b = clip._source[1].resize(size, interpolation = interpolation)
        return a.slide(b, origin = clip._origin, frameCount = clip._frameCount, fValues = clip._fValues, transitionOnly = True)
      elif isinstance(clip, vfx.composite.CompositeVideoClip):
        # ResizedVideoClip_↓ < CompositeVideoClip
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        bg = clip._source[0]
        fg = clip._source[1]
        fgSize = (round(fg.width * width / bg.width), round(fg.height * height / bg.height))
        if fgSize[0] < 1 or fgSize[1] < 1:
          return bg.resize(size, interpolation = interpolation)
        x = clip._x1 * width / bg.width
        y = clip._y1 * height / bg.height
        return bg.resize(size, interpolation = interpolation).composite(fg.resize(fgSize, interpolation = interpolation), x1 = x, y1 = y)
      elif isinstance(clip, vfx.concat.ConcatenatedVideoClip):
        # ResizedVideoClip_↓ < ConcatenatedVideoClip
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return (clip._source[0].resize(size, interpolation = interpolation)).concat([s.resize(size, interpolation = interpolation) for s in clip._source[1:]])



  # Source: A single VideoClip to be resized
  source = (clip,)

  # Metadata: Update the dimensions
  metadata = copy.copy(clip._metadata)
  metadata.size = (width, height)

  return ResizedVideoClip(source, metadata, interpolation)



class ResizedVideoClip(VideoClip):
  """ResizedVideoClip(source, metadata)

  Represents a video clip that has had its frame width and height changed.
  """



  def __init__(self, source, metadata, interpolation):
    super().__init__(source, metadata, isConstant = source[0]._isConstant)

    self._interpolation = interpolation



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__(), self._interpolation))



  def _pseudoeq(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super()._pseudoeq(other):
        # The interpolation modes must be the same
        if self._interpolation == other._interpolation:
          return True

    return False



  def __eq__(self, other):
    return self._pseudoeq(other) and self._source == other._source



  def _framegen(self, n):
    image = self._source[0].frame(n)
    return cv2.resize(image, self.size, interpolation = self._interpolation)
