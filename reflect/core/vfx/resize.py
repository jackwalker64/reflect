# -*- coding: utf-8 -*-

from ..clips import VideoClip
import cv2



def resize(clip, size = None, width = None, height = None):
  """resize(clip, size = None, width = None, height = None)

  Returns a copy of `clip` with the new frame dimensions.

  Examples
  --------
  >>> clip.resize((1280, 720))                 # 1280×720
  >>> clip.resize(0.5)                         # (0.5*oldWidth)×(0.5*oldHeight)
  >>> clip.resize(width = 1280)                # 1280×? where ? is computed automatically to preserve aspect ratio
  >>> clip.resize(height = 720)                # ?×720 where ? is computed automatically to preserve aspect ratio
  >>> clip.resize(width = 1280, height = 1024) # 1280×1024
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("resize requires a clip of type VideoClip")

  # Process the arguments
  (oldWidth, oldHeight) = clip.size
  if size != None:
    if width != None or height != None:
      raise TypeError("either specify size, or specify at least one of width and height")
    elif type(size) == int or type(size) == float:
      (width, height) = (round(oldWidth * size), round(oldHeight * size))
    elif type(size) == tuple:
      (width, height) = size
    else:
      raise TypeError("size must be either an int, a float, or a (width, height) pair")
  else:
    if width != None and height != None:
      pass
    elif width != None and height == None:
      height = round(width / oldWidth * oldHeight)
    elif width == None and height != None:
      width = round(height / oldHeight * oldWidth)
    else:
      raise TypeError("resize requires either size, width, or height to be provided")

  # Source: A single VideoClip to be resized
  source = (clip,)

  # Framegen: Resize each frame to the specified dimensions
  def framegen(n):
    image = source[0].frame(n)
    return cv2.resize(image, (width, height), interpolation = cv2.INTER_AREA)

  metadata = clip.metadata.copy()
  metadata["size"] = (width, height)

  return VideoClip(source, framegen, metadata)
