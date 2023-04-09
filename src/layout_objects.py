#!/usr/bin/python3
'''
Class for intermediate layout objects
'''

from .utils import get_image_size
from .defines import DEFAULT_SIZE, TagType
from typing import Any, Dict
from dataclasses import dataclass


# Represents the interface for grouping the structural objects
class LPTag:
    pass


@dataclass
class Pop(LPTag):
    target: TagType
    type: TagType = TagType.POP

    def __repr__(self):
        return f'<Pop {self.target}>'


@dataclass
class LPMeme(LPTag):
    image: str | None = None
    # note: under the hood, `/WP:/`` adds an LPMeme with size=('lookahead', None)
    size: tuple[int | str | None, int | None] = (None, None)
    fillcolor: str = 'white'
    gridposition: str | None = None
    mode: str = "resize"
    type: TagType = TagType.MEME

    def __repr__(self):
        coords = f'({self.size[0]}x{self.size[1]})' if self.size else f'(?x?)'
        return f'<Meme: {self.image} {coords} @{self.gridposition}>'


@dataclass
class LPText(LPTag):
    text: str
    position: str | None = None
    rotation: int = 0
    type: TagType = TagType.TEXT

    def __repr__(self):
        return f'<Text "{self.text}" @{self.position}>'


@dataclass
class LPComposite(LPTag):
    gridsize: tuple[int, int] | None = None
    gridposition: str | None = None
    type: TagType | None = TagType.COMPOSITE

    def __repr__(self):
        return f'<LPComposite: {self.gridsize} @{self.gridposition}>'


@dataclass
class LPWhitespacePrefix(LPTag):
    text: str
    type: TagType = TagType.WHITESPACE

    def __repr__(self):
        return f'<WP: {self.text}>'
