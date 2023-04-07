#!/usr/bin/python3
'''
Class for intermediate layout objects
'''

from .utils import get_image_size
from .defines import DEFAULT_SIZE, TagType
from typing import Any, Dict
from dataclasses import dataclass


class Pop:
    def __init__(self, tag: TagType):
        self.type = TagType.POP
        self.target = tag

    def __repr__(self):
        return f'<Pop {self.target}>'


@dataclass
class LPMeme:
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
class LPText:
    text: str
    position: str | None = None
    rotation: int = 0
    type: TagType = TagType.TEXT

    def __repr__(self):
        return f'<Text "{self.text}" @{self.position}>'


@dataclass
class LPComposite:
    gridsize: Any | None = None  # TODO(schorrm): fix with correct types
    gridposition: Any | None = None  # TODO(schorrm): fix with correct type
    type: TagType | None = TagType.COMPOSITE

    def __repr__(self):
        return f'<LPComposite: {self.gridsize} @{self.gridposition}>'


class LPWhitespacePrefix:
    def __init__(self, text):
        self.text = text
        self.type = TagType.WHITESPACE

    def __repr__(self):
        return f'<WP: {self.text}>'

# class LPOutput:
#     def __init__(self, tagtype: TagType, data: Dict):
#         self.type = tagtype
#         self.data = data

#     def __getattr__(self, attr):
#         if attr in self.data.keys():
#             return self.data[attr]
#         else:
#             raise ???
