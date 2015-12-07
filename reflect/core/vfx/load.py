# -*- coding: utf-8 -*-

from ..clips import VideoClip, VideoClipMetadata, clipMethod, memoizeHash
import os
import imageio



@clipMethod
def load(filepath):
  """load(filepath)

  Constructs and returns a Clip object representing the media at `filepath`.
  The type of Clip returned depends on the kind of file.
  """

  if not os.path.exists(filepath):
    raise IOError("The file \"{}\" does not exist.".format(os.path.realpath(filepath)))

  # (currently assuming the file is a video file)
  reader = imageio.get_reader(filepath)

  source = filepath

  md = reader.get_meta_data()
  metadata = VideoClipMetadata(md["size"], md["nframes"], md["fps"])

  return LoadedVideoClip(source, metadata, reader)



class LoadedVideoClip(VideoClip):
  """LoadedVideoClip(source, metadata)

  Represents a video clip sourced directly from a video file.
  """



  def __init__(self, source, metadata, reader):
    super().__init__(source, metadata)

    self._reader = reader



  def __del__(self):
    self._reader.close()



  @memoizeHash
  def __hash__(self):
    return hash(self._reader.request.filename)



  def __eq__(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The readers must be reading the same file
      if self._reader.request.filename == other._reader.request.filename:
        return True

    return False



  def _framegen(self, n):
    return self._reader.get_data(n)
