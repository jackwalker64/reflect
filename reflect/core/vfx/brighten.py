# -*- coding: utf-8 -*-

from ..clips import VideoClip, clipMethod, memoizeHash
import copy



@clipMethod
def brighten(clip, amount):
  """brighten(clip, amount)

  Returns a copy of `clip` where every frame has been brightened/darkened by the specified amount.

  Examples
  --------
  >>> clip.brighten(5)    # Add 5 to each of the rgb values, making the images brighter
  >>> clip.brighten(0)    # No effect
  >>> clip.brighten(-5)   # Subtract 5 from each of the rgb values, making the images darker
  >>> clip.brighten(255)  # Guarantee that the resulting frames are entirely white
  >>> clip.brighten(-255) # Guarantee that the resulting frames are entirely black
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("brighten requires a clip of type VideoClip")

  # Process the arguments
  if not isinstance(amount, int) and not isinstance(amount, float):
    raise TypeError("expected amount to be an int or a float, but instead received a {}".format(type(amount)))
  if amount < -1 or amount > 1:
    raise ValueError("amount must be between -1 and 1 inclusive")

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



  def __eq__(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super().__eq__(other):
        # The parameter must be the same
        if self._amount == other._amount:
          return True

    return False



  def _framegen(self, n):
    amount = self._amount
    image = self._source[0].frame(n)

    if amount >= 0:
      # Brighten
      image = image * (1 - amount) + (amount * 255)
    else:
      # Darken
      image = image * (1 + amount)

    return image
