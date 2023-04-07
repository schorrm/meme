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
    size: tuple[int | None, int | None] = (None, None)
    fillcolor: str = 'white'
    position: str | None = None
    gridposition: str | None = position
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
    gridsize: Any | None = None  # TODO(schorrm): fix with correct types
    gridposition: Any | None = None  # TODO(schorrm): fix with correct type
    type: TagType | None = TagType.COMPOSITE

    def __repr__(self):
        return f'<LPComposite: {self.gridsize} @{self.gridposition}>'


@dataclass
class LPWhitespacePrefix(LPTag):
    text: str
    type: TagType = TagType.WHITESPACE

    def __repr__(self):
        return f'<WP: {self.text}>'
