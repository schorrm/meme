#!/usr/bin/python3

from dataclasses import dataclass, field
from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont
from .defines import TagType, DEFAULT_FONT_SIZE


def _STATIC(tag: TagType) -> TagType:
    return field(init=False, default=tag)


@dataclass
class Font:
    font_face: str = 'Impact'
    font_size: int = DEFAULT_FONT_SIZE
    outline_size: int = 2
    text_style: str = 'r'
    type: TagType = _STATIC(TagType.FONT)
    _cached_font: FreeTypeFont | None = field(init=False, default=None)

    @property
    def PIL_font(self):
        """ Return PIL.ImageFont instance """
        if not self._cached_font:
            try:
                self._cached_font = ImageFont.truetype(
                    font=self.font_face, size=self.font_size)
            except OSError:
                # re-raise with a diagnostic so you can find the missing font..
                raise OSError(f"Couldn't find font '{self.font_face}'")
        return self._cached_font

    def inherit_from(self, update_font):
        if self.outline_size == None:  # Zero is a size, none is not
            self.outline_size = update_font.outline_size
        self.font_size = self.font_size or update_font.font_size
        self.font_face = self.font_face or update_font.font_face
        self.text_style = self.text_style or update_font.text_style
        return self

    def __repr__(self):
        return f'<Font: {self.font_face} {self.font_size}{self.text_style}, {self.outline_size}>'


@dataclass
class Alignment:
    halign: str = 'center'
    valign: str = 'center'
    type: TagType = _STATIC(TagType.ALIGNMENT)

    def inherit_from(self, update_alignment):
        self.halign = self.halign or update_alignment.halign
        self.valign = self.valign or update_alignment.valign
        return self

    def __repr__(self):
        return f'<Align {self.halign}, {self.valign}>'


@dataclass
class Color:
    foreground: str = "black"
    background: str | None = None
    outline: str = "white"
    type: TagType = _STATIC(TagType.COLOR)

    def inherit_from(self, update_color):
        self.foreground = self.foreground or update_color.foreground
        self.background = self.background or update_color.background
        self.outline = self.outline or update_color.outline
        return self

    def __repr__(self):
        return f'<Color: FG={self.foreground}, BG={self.background}, OL={self.outline}>'


@dataclass
class Time:
    frames: tuple[int | None, int | None] | None = None
    seconds: tuple[float | None, float | None] | None = None
    type: TagType = _STATIC(TagType.TIME)


# TODO: Support text style -- we need to figure a lot of other details here, may need tweaks
# Not guaranteed support in 1.0
class TextStyle:
    def __init__(self, bold: bool = False, italic: bool = False, underline: bool = False, strikethrough: bool = False):
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strikethrough = strikethrough
        self.type = TagType.TEXTSTYLE
