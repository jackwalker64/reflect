# -*- coding: utf-8 -*-

from ..clips import VideoClip, VideoClipMetadata, clipMethod, memoizeHash
import os
import imageio
import collections



# Keeps track of open readers
openReaders = {}
readyReaders = {}



@clipMethod
def load(filepath):
  """load(filepath)

  Constructs and returns a VideoClip object representing the media at `filepath`.
  """

  if not os.path.exists(filepath):
    raise IOError("The file \"{}\" does not exist.".format(os.path.realpath(filepath)))

  if filepath in readyReaders:
    # Instead of creating a new ffmpeg process, reuse an existing one
    reader = readyReaders[filepath].popleft()
    if len(readyReaders[filepath]) == 0:
      del readyReaders[filepath]
  else:
    reader = imageio.get_reader(filepath)

  if filepath in openReaders:
    openReaders[filepath].append(reader)
  else:
    # Create a queue to hold all open readers of this file.
    # A queue (as opposed to a stack) is used here so that LoadedVideoClips are more likely to pop
    # readers that were used by equivalent LoadedVideoClips in the previous session.
    openReaders[filepath] = collections.deque([reader])

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
