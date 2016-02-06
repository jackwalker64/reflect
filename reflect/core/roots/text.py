# -*- coding: utf-8 -*-

from ..clips import ImageClip, clipMethod, memoizeHash
import copy
import numpy
import pygame
import os



@clipMethod
def text(text, font = None, size = 12, color = (0, 0, 0), background = None, bold = False, italic = False, underline = False, antialias = True):
  """text(text, font = None, size = 12, color = (0, 0, 0), background = None, bold = False, italic = False, underline = False, antialias = True)

  Returns an image clip with the string `text` rendered with the given parameters.

  Examples
  --------
  >>> reflect.text("hello world", font = "arial", size = 12, bold = True)
  >>> reflect.text("hello world", font = "D:/droidsans.ttf", size = 12, bold = True)
  """

  if font is None:
    font = pygame.font.get_default_font()

  fontPath = font
  if not os.path.exists(fontPath):
    fontPath = pygame.font.match_font(font)
    if fontPath is None:
      raise ValueError("failed to find the font \"{}\"".format(font))
  fontPath = os.path.realpath(fontPath)

  pygameFont = pygame.font.Font(fontPath, size)
  pygameFont.set_bold(bold)
  pygameFont.set_italic(italic)
  pygameFont.set_underline(underline)

  # surface = pygameFont.render(text, antialias, color, background)

  return TextImageClip(pygameFont, fontPath, size,  text, antialias, color, background)



class TextImageClip(ImageClip):
  """TextImageClip(pygameFont, fontPath, fontSize, text, antialias, color, background)

  Represents an image of a rendered string of text.
  """



  def __init__(self, pygameFont, fontPath, fontSize, text, antialias, color, background):
    super().__init__(None, pygameFont.size(text))

    self._pygameFont = pygameFont
    self._fontPath = fontPath
    self._fontSize = fontSize
    self._text = text
    self._antialias = antialias
    self._color = color
    self._background = background



  @memoizeHash
  def __hash__(self):
    return hash((super().__hash__(), self._fontPath, self._fontSize, self._text, self._antialias, self._color, self._background))



  def _pseudoeq(self, other):
    # self and other must both be of this class
    if type(other) == type(self):
      # The parent class parts must be the same
      if super()._pseudoeq(other):
        # The parameters (except for the pygame font object) must be the same
        if (self._fontPath, self._fontSize, self._text, self._antialias, self._color, self._background) == (other._fontPath, other._fontSize, other._text, other._antialias, other._color, other._background):
          return True

    return False



  def __eq__(self, other):
    return self._pseudoeq(other) and self._source == other._source



  def _imagegen(self):
    # TODO: support multiline text by rendering each line individually (and position according to a new align parameter)
    surface = self._pygameFont.render(self._text, self._antialias, self._color, self._background).convert_alpha()

    # TODO: set the mask from pygame.surfarray.array_alpha(surface).swapaxes(0, 1)
    image = pygame.surfarray.array3d(surface).swapaxes(0, 1)

    return image
