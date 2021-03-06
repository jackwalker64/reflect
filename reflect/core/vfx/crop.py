# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import copy



@clipMethod
def crop(clip, x1 = None, y1 = None, x2 = None, y2 = None, xc = None, yc = None, width = None, height = None):
  """crop(clip, x1 = None, y1 = None, x2 = None, y2 = None, xc = None, yc = None, width = None, height = None)

  Returns a rectangular subregion of `clip`.

  Examples
  --------
  >>> clip.crop(x1 = 100, y1 = 100, x2 = 300, y2 = 200)        # conserves a 200×100 region with the top-left pixel at (100, 100)
  >>> clip.crop(x1 = clip.width / 2)                           # conserves the right-hand half of the clip
  >>> clip.crop(xc = 960, yc = 540, width = 100, height = 100) # conserves a 100×100 box centred about (960, 540)
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("crop requires a clip of type VideoClip")

  # If width was passed as an argument, then use it to deduce x1 and/or x2
  if width is not None:
    if x1 is not None:
      if x2 is not None:
        if x1 + width != x2:
          raise ValueError("inconsistent arguments: x1 = {}, x2 = {}, width = {}".format(x1, x2, width))
      else:
        x2 = x1 + width
    elif x2 is not None:
      x1 = x2 - width
    elif xc is not None:
      x1 = xc - width / 2
      x2 = xc + width / 2
    else:
      x1 = 0
      x2 = width

  # If height was passed as an argument, then use it to deduce y1 and/or y2
  if height is not None:
    if y1 is not None:
      if y2 is not None:
        if y1 + height != y2:
          raise ValueError("inconsistent arguments: y1 = {}, y2 = {}, height = {}".format(y1, y2, height))
      else:
        y2 = y1 + height
    elif y2 is not None:
      y1 = y2 - height
    elif yc is not None:
      y1 = yc - height / 2
      y2 = yc + height / 2
    else:
      y1 = 0
      y2 = height

  if x1 is None:
    x1 = 0
  if y1 is None:
    y1 = 0
  if x2 is None:
    x2 = clip.width
  if y2 is None:
    y2 = clip.height

  x1 = int(x1)
  y1 = int(y1)
  x2 = int(x2)
  y2 = int(y2)

  # Check that the user-specified region is within the source clip's boundaries
  if x1 < 0:
    raise ValueError("the crop region exceeds the clip's left boundary by {} pixels (x1 = {})".format(-x1, x1))
  if y1 < 0:
    raise ValueError("the crop region exceeds the clip's top boundary by {} pixels (y1 = {})".format(-y1, y1))
  if x2 > clip.width:
    raise ValueError("the crop region exceeds the clip's right boundary by {} pixels (x2 = {})".format(x2 - clip.width, x2))
  if y2 > clip.height:
    raise ValueError("the crop region exceeds the clip's bottom boundary by {} pixels (y2 = {})".format(y2 - clip.height, y2))

  if y2 <= y1:
    raise ValueError("the crop region is invalid (y1 = {}, y2 = {})".format(y1, y2))
  if x2 <= x1:
    raise ValueError("the crop region is invalid (x1 = {}, x2 = {})".format(x1, x2))

  if x1 == 0 and y1 == 0 and x2 == clip.width and y2 == clip.height:
    return clip

  # Push
  from ..clips import transformations
  if "CanonicalOrder" in transformations:
    from reflect.core import vfx
    if isinstance(clip, vfx.crop.CroppedVideoClip):
      # CroppedVideoClip = CroppedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].crop(clip._x1 + x1, clip._y1 + y1, clip._x1 + x2, clip._y1 + y2)
    elif isinstance(clip, vfx.resize.ResizedVideoClip):
      # CroppedVideoClip < ResizedVideoClip_↓
      # CroppedVideoClip < ResizedVideoClip_↑
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      (wScale, hScale) = (clip.width / clip._source[0].width, clip.height / clip._source[0].height)
      return clip._source[0].crop(x1/wScale, y1/hScale, x2/wScale, y2/hScale).resize(size = (x2 - x1, y2 - y1), interpolation = clip._interpolation)
    elif isinstance(clip, vfx.brighten.BrightenedVideoClip):
      # CroppedVideoClip < BrightenedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].crop(x1, y1, x2, y2).brighten(clip._amount)
    elif isinstance(clip, vfx.greyscale.GreyscaleVideoClip):
      # CroppedVideoClip < GreyscaleVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].crop(x1, y1, x2, y2).greyscale()
    elif isinstance(clip, vfx.blur.BlurredVideoClip):
      # CroppedVideoClip | BlurredVideoClip
      pass
    elif isinstance(clip, vfx.gaussianBlur.GaussianBlurredVideoClip):
      # CroppedVideoClip | GaussianBlurredVideoClip
      pass
    elif isinstance(clip, vfx.rate.ChangedRateVideoClip):
      # CroppedVideoClip < ChangedRateVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].crop(x1, y1, x2, y2).rate(clip.fps)
    elif isinstance(clip, vfx.reverse.ReversedVideoClip):
      # CroppedVideoClip < ReversedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].crop(x1, y1, x2, y2).reverse()
    elif isinstance(clip, vfx.speed.SpedVideoClip):
      # CroppedVideoClip < SpedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].crop(x1, y1, x2, y2).speed(clip._scale)
    elif isinstance(clip, vfx.subclip.SubVideoClip):
      # CroppedVideoClip < SubVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].crop(x1, y1, x2, y2).subclip(clip._n1, clip._n2)
    elif isinstance(clip, vfx.slide.SlideTransitionVideoClip):
      # CroppedVideoClip < SlideTransitionVideoClip
      a = clip._source[0].crop(x1, y1, x2, y2)
      b = clip._source[1].crop(x1, y1, x2, y2)
      if clip._origin in ("left", "right"):
        fValues = [max(0, min(x2, clip._fValues[t]*clip.width) - x1)/(x2 - x1) for t in range(len(clip._fValues))]
      else:
        fValues = [max(0, min(y2, clip._fValues[t]*clip.height) - y1)/(y2 - y1) for t in range(len(clip._fValues))]
      return a.slide(b, origin = clip._origin, frameCount = clip._frameCount, fValues = fValues, transitionOnly = True)
    elif isinstance(clip, vfx.composite.CompositeVideoClip):
      # CroppedVideoClip < CompositeVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      bg = clip._source[0]
      fg = clip._source[1]
      (cx1, cy1, cx2, cy2) = (clip._x1, clip._y1, clip._x1 + fg.width, clip._y1 + fg.height)
      q1 = ((x1 < cx1) << 3) | ((x1 > cx2) << 2) | ((y1 < cy1) << 1) | ((y1 > cy2) << 0)
      q2 = ((x2 < cx1) << 3) | ((x2 > cx2) << 2) | ((y2 < cy1) << 1) | ((y2 > cy2) << 0)
      if q1 == 0 and q2 == 0:
        # Case 1: The crop region is inside the foreground clip region
        return fg.crop(x1 - cx1, y1 - cy1, x2 - cx1, y2 - cy1)
      elif q1 & q2 != 0:
        # Case 2: The crop region is outside the foreground clip region
        return bg.crop(x1, y1, x2, y2)
      else:
        # Case 3: The crop region touches the foreground clip's edge
        fgCropRegion = (
          max(0, x1 - cx1),
          max(0, y1 - cy1),
          min(fg.width, x2 - cx1),
          min(fg.height, y2 - cy1)
        )
        newCompositePoint = (
          max(0, cx1 - x1),
          max(0, cy1 - y1)
        )
        return bg.crop(x1, y1, x2, y2).composite(
          fg.crop(fgCropRegion[0], fgCropRegion[1], fgCropRegion[2], fgCropRegion[3]),
          x1 = newCompositePoint[0],
          y1 = newCompositePoint[1]
        )
    elif isinstance(clip, vfx.concat.ConcatenatedVideoClip):
      # CroppedVideoClip < ConcatenatedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return (clip._source[0].crop(x1, y1, x2, y2)).concat([s.crop(x1, y1, x2, y2) for s in clip._source[1:]])

  # Source: A single VideoClip to be cropped
  source = (clip,)

  # Metadata: Update the dimensions
  metadata = copy.copy(clip._metadata)
  metadata.size = (x2 - x1, y2 - y1)

  return CroppedVideoClip(source, metadata, x1 = x1, y1 = y1, x2 = x2, y2 = y2)



class CroppedVideoClip(VideoClip):
  """CroppedVideoClip(source, metadata, x1, y1, x2, y2)

  Represents a subregion of a video clip.
  """



  def __init__(self, source, metadata, x1, y1, x2, y2):
    super().__init__(source, metadata, isIndirection = True, isConstant = source[0]._isConstant)

    self._x1 = x1
    self._y1 = y1
    self._x2 = x2
    self._y2 = y2



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__(), (self._x1, self._y1, self._x2, self._y2)))



  def _pseudoeq(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super()._pseudoeq(other):
        # The crop regions must be the same
        if (self._x1, self._y1, self._x2, self._y2) == (other._x1, other._y1, other._x2, other._y2):
          return True

    return False



  def __eq__(self, other):
    return self._pseudoeq(other) and self._source == other._source



  def _framegen(self, n):
    image = self._source[0].frame(n)
    return image[self._y1:self._y2, self._x1:self._x2]
