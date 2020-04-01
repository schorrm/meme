#!/usr/bin/python3

from PIL import ImageFont
from defines import TagType, DEFAULT_FONT_SIZE

class Font:
    def __init__(self, font_face='impact', font_size=DEFAULT_FONT_SIZE, outline_size=0, text_style='r'):
        self.font_face = font_face
        self.font_size = font_size
        self.outline_size = outline_size
        self.text_style = text_style
        self._cached_font = None
        self.type = TagType.FONT

    @property
    def PIL_font(self):
        """ Return PIL.ImageFont instance """
        if not self._cached_font:
            self._cached_font = ImageFont.truetype(font=self.font_face, size=self.font_size)
        return self._cached_font

    def inherit_from(self, update_font):
        if self.outline_size == None: # Zero is a size, none is not
            self.outline_size = update_font.outline_size
        self.font_size = self.font_size or update_font.font_size
        self.font_face = self.font_face or update_font.font_face
        self.text_style = self.text_style or update_font.text_style
        return self

    def __repr__(self):
        return f'<Font: {self.font_face} {self.font_size}{self.text_style}, {self.outline_size}>'


class Alignment:
    def __init__(self, halign: str = 'center', valign: str = 'center'):
        self.halign = halign
        self.valign = valign
        self.type = TagType.ALIGNMENT

    def inherit_from(self, update_alignment):
        self.halign = self.halign or update_alignment.halign
        self.valign = self.valign or update_alignment.valign
        return self

    def __repr__(self):
        return f'<Align {self.halign}, {self.valign}>'


class Color:
    def __init__(self, foreground: str = "black", background: str = None, outline: str = "white"):
        self.foreground = foreground
        self.background = background
        self.outline = outline
        self.type = TagType.COLOR

    def inherit_from(self, update_color):
        self.foreground = self.foreground or update_color.foreground
        self.background = self.background or update_color.background
        self.outline = self.outline or update_color.outline
        return self

    def __repr__(self):
        return f'<Color: FG={self.foreground}, BG={self.background}, OL={self.outline}>'


# TODO: Support text style -- we need to figure a lot of other details here, may need tweaks
# Not guaranteed support in 1.0
class TextStyle:
    def __init__(self, bold: bool = False, italic: bool = False, underline: bool = False, strikethrough: bool = False):
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strikethrough = strikethrough
        self.type = TagType.TEXTSTYLE
