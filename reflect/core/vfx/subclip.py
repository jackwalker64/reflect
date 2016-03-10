# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
from ..util import timecodeToFrame, interpretSubclipParameters
import copy



@clipMethod
def subclip(clip, n1 = None, n2 = None, frameCount = None, t1 = None, t2 = None, duration = None):
  """subclip(clip, n1 = None, n2 = None, frameCount = None, t1 = None, t2 = None, duration = None)

  Returns a contiguous subsequence of the frames of `clip`.

  The subsequence can be specified either by timecodes (t1 and/or t2 and/or duration),
  or by frame numbers (n1 and/or n2 and/or frameCount).

  Examples
  --------
  >>> clip.subclip(10)               # Conserves frames after the 10 second mark
  >>> clip.subclip("01:00", 5)       # Produces a 5 second clip starting at 1 minute in
  >>> clip.subclip(n1 = 42, n2 = 52) # Produces a clip containing only 10 frames (42..51 inclusive)
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("expected a clip of type VideoClip")

  # Convert timecodes
  if t1 is not None:
    if n1 is not None:
      raise TypeError("expected at most one of t1 and n1, but received both")
    else:
      n1 = timecodeToFrame(t1, clip.fps)
  if t2 is not None:
    if n2 is not None:
      raise TypeError("expected at most one of t2 and n2, but received both")
    else:
      n2 = timecodeToFrame(t2, clip.fps)
  if duration is not None:
    if frameCount is not None:
      raise TypeError("expected at most one of duration and frameCount, but received both")
    else:
      frameCount = timecodeToFrame(duration, clip.fps)

  # Deduce (n1, n2)
  if n1 is not None:
    if n2 is not None:
      if frameCount is not None:
        raise TypeError("expected at most two of n1, n2, frameCount, but received all three")
    else:
      if frameCount is not None:
        n2 = n1 + frameCount
      else:
        n2 = clip.frameCount
  elif n2 is not None:
    if frameCount is not None:
      n1 = n2 - frameCount
    else:
      n1 = 0
  elif frameCount is not None:
    n1 = 0
    n2 = frameCount
  else:
    raise TypeError("insufficient arguments provided")

  (n1, n2) = interpretSubclipParameters(n1, n2, clip.frameCount)

  if n1 == 0 and n2 == clip.frameCount:
    return clip

  # Push
  from ..clips import transformations
  if "CanonicalOrder" in transformations:
    from reflect.core import vfx
    if isinstance(clip, vfx.crop.CroppedVideoClip):
      # SubVideoClip > CroppedVideoClip
      pass
    elif isinstance(clip, vfx.resize.ResizedVideoClip):
      if clip.width * clip.height >= clip._source[0].width * clip._source[0].height:
        # SubVideoClip < ResizedVideoClip_↑
        if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
        return clip._source[0].subclip(n1, n2).resize(clip.size, interpolation = clip._interpolation)
      else:
        # SubVideoClip > ResizedVideoClip_↓
        pass
    elif isinstance(clip, vfx.brighten.BrightenedVideoClip):
      # SubVideoClip > BrightenedVideoClip
      pass
    elif isinstance(clip, vfx.greyscale.GreyscaleVideoClip):
      # SubVideoClip > GreyscaleVideoClip
      pass
    elif isinstance(clip, vfx.blur.BlurredVideoClip):
      # SubVideoClip > BlurredVideoClip
      pass
    elif isinstance(clip, vfx.gaussianBlur.GaussianBlurredVideoClip):
      # SubVideoClip > GaussianBlurredVideoClip
      pass
    elif isinstance(clip, vfx.rate.ChangedRateVideoClip):
      # SubVideoClip > ChangedRateVideoClip
      pass
    elif isinstance(clip, vfx.reverse.ReversedVideoClip):
      # SubVideoClip > ReversedVideoClip
      pass
    elif isinstance(clip, vfx.speed.SpedVideoClip):
      # SubVideoClip > SpedVideoClip
      pass
    elif isinstance(clip, vfx.subclip.SubVideoClip):
      # SubVideoClip = SubVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      return clip._source[0].subclip(clip._n1 + n1, clip._n1 + n2)
    elif isinstance(clip, vfx.slide.SlideTransitionVideoClip):
      # SubVideoClip < SlideTransitionVideoClip
      # if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      # a = clip._source[0].subclip(n1, n2)
      # b = clip._source[1].subclip(n1, n2)
      # return a.slide(b, origin = clip._origin, frameCount = int(clip._frameCount / scale), fValues = clip._fValues, transitionOnly = True)
      raise NotImplementedError()
    elif isinstance(clip, vfx.composite.CompositeVideoClip):
      # SubVideoClip | CompositeVideoClip
      pass
    elif isinstance(clip, vfx.concat.ConcatenatedVideoClip):
      # SubVideoClip < ConcatenatedVideoClip
      if clip._childCount == 0 and clip._graph.isLeaf(clip): clip._graph.removeLeaf(clip)
      from bisect import bisect_left
      firstClipIndex = bisect_left(clip.sourceStartFrames, n1 + 1)
      secondClipIndex = bisect_left(clip.sourceStartFrames, n2)
      if firstClipIndex == 0:
        firstClipOffset = n1
      else:
        firstClipOffset = n1 - clip.sourceStartFrames[firstClipIndex - 1]
      if secondClipIndex == 0:
        secondClipOffset = n2
      else:
        secondClipOffset = n2 - clip.sourceStartFrames[secondClipIndex - 1]
      if firstClipIndex == secondClipIndex:
        return clip._source[firstClipIndex].subclip(firstClipOffset, secondClipOffset)
      else:
        firstClip = clip._source[firstClipIndex].subclip(firstClipOffset)
        middleClips = clip._source[firstClipIndex+1:secondClipIndex]
        lastClip = clip._source[secondClipIndex].subclip(0, secondClipOffset)
        tailClips = list(middleClips)
        tailClips.append(lastClip)
        return firstClip.concat(tailClips)

  # Source: A single VideoClip
  source = (clip,)

  # Metadata: Update the duration
  metadata = copy.copy(clip._metadata)
  metadata.frameCount = n2 - n1

  return SubVideoClip(source, metadata, n1 = n1, n2 = n2)



class SubVideoClip(VideoClip):
  """SubVideoClip(source, metadata, n1, n2)

  Represents a contiguous subsequence [n1, n2) of frames of another video clip.
  """



  def __init__(self, source, metadata, n1, n2):
    super().__init__(source, metadata, isIndirection = True, isConstant = source[0]._isConstant)

    self._n1 = n1
    self._n2 = n2



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__(), (self._n1, self._n2)))



  def _pseudoeq(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super()._pseudoeq(other):
        # The subclip regions must be the same
        if (self._n1, self._n2) == (other._n1, other._n2):
          return True

    return False



  def __eq__(self, other):
    return self._pseudoeq(other) and self._source == other._source



  def _framegen(self, n):
    clip = self._source[0]

    n1 = self._n1
    n2 = self._n2

    requestedFrame = n + n1
    if n < 0:
      raise IndexError("received a request for a frame with a negative index ({})".format(n))
    elif n >= n2 - n1:
      raise IndexError("received a request for the frame at index {}, but this subclip only contains {} frames".format(n, n2 - n1))

    image = clip.frame(requestedFrame)

    return image
