# -*- coding: utf-8 -*-

from ..clips import VideoClip, VideoClipMetadata, ImageClip, clipMethod, memoizeHash
import os
import imageio
import collections



# Keeps track of open readers
openReaders = {}
readyReaders = {}



@clipMethod
def load(filepath):
  """load(filepath)

  Constructs and returns a VideoClip or ImageClip object representing the media at `filepath`.
  """

  if not os.path.exists(filepath):
    raise IOError("The file \"{}\" does not exist.".format(os.path.realpath(filepath)))



  if filepath in readyReaders:
    # Instead of creating a new reader process, reuse an existing one
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

  if "I" in reader.format.modes:
    # imageio has determined that the file can be read as a video (sequence of images)
    source = filepath
    md = reader.get_meta_data()
    metadata = VideoClipMetadata(md["size"], md["nframes"], md["fps"])
    return LoadedVideoClip(source, metadata, reader)
  elif "i" in reader.format.modes:
    # imageio has determined that the file can be read as a single image
    return LoadedImageClip(filepath, reader)
  else:
    raise ValueError("The filetype of \"{}\" is unsupported.".format(filepath))



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



class LoadedImageClip(ImageClip):
  """LoadedImageClip(filepath, reader)

  Represents a single image sourced directly from an image file.
  """



  def __init__(self, filepath, reader):
    # Before calling ImageClip.__init__, we need to determine the image dimensions
    self._reader = reader
    self._filepath = filepath
    size = self._dimensions()
    if size is None:
      raise Exception("Failed to determine the dimensions of {}".format(filepath))

    super().__init__(filepath, size)



  def _dimensions(self):
    import struct
    import imghdr
    with open(self._filepath, "rb") as fhandle:
      head = fhandle.read(24)
      if len(head) != 24:
        return
      if imghdr.what(self._filepath) == "png":
        check = struct.unpack(">i", head[4:8])[0]
        if check != 0x0d0a1a0a:
          return
        width, height = struct.unpack(">ii", head[16:24])
      elif imghdr.what(self._filepath) == "gif":
        width, height = struct.unpack("<HH", head[6:10])
      elif imghdr.what(self._filepath) == "jpeg":
        try:
          fhandle.seek(0) # Read 0xff next
          size = 2
          ftype = 0
          while not 0xc0 <= ftype <= 0xcf:
            fhandle.seek(size, 1)
            byte = fhandle.read(1)
            while ord(byte) == 0xff:
              byte = fhandle.read(1)
            ftype = ord(byte)
            size = struct.unpack(">H", fhandle.read(2))[0] - 2
          # We are at a SOFn block
          fhandle.seek(1, 1)  # Skip `precision" byte.
          height, width = struct.unpack(">HH", fhandle.read(4))
        except Exception: #IGNORE:W0703
          return
      else:
        return
      return width, height



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__(), self._filepath))



  def __eq__(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super().__eq__(other):
        # The readers must be reading the same file
        if self._reader.request.filename == other._reader.request.filename:
          return True

    return False



  def _imagegen(self):
    print("gen {}".format(self))
    image = self._reader.get_data(0) # Load the image into memory
    return image
