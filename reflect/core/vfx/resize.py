# -*- coding: utf-8 -*-

from ..clips import VideoClip



def resize(clip, size = None, width = None, height = None):
  """resize(clip, size = None, width = None, height = None)

  Returns a copy of `clip` with the new frame dimensions.
  """

  if not isinstance(clip, VideoClip):
    raise TypeError("resize requires a clip of type VideoClip")

  source = clip

  def framegen(n):
    print("n = {}".format(n))
    print("width = {}".format(width))
    # TODO: implement framegen to return resized frames, by calling the source's frame method (not its framegen method) and then resizing it here.

  metadata = clip.metadata.copy()
  # TODO: update the metadata with the new size

  # TODO: set my graph to my parent's graph, and pass it to the VideoClip constructor

  return VideoClip(source, framegen, metadata)
