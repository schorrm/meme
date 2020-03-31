#!/usr/bin/python3
'''
Class for intermediate layout objects
'''

from utils import get_image_size, DEFAULT_SIZE, TagType
from typing import Dict

class Pop:
    def __init__(self, tag: TagType):
        self.tag = tag

    def __repr__(self):
        return f'<Pop {self.tag}>'


class LPMeme:
    def __init__(self, image: str = None, size=None, fillcolor='white', position=None):
        self.image = image
        self.size = size
        self.fillcolor = fillcolor
        self.gridposition = position

    def __repr__(self):
        coords = f'({self.size[0]}x{self.size[1]})' if self.size else f'(?x?)'
        return f'<Meme: {self.image} {coords} @{self.gridposition}>'

class LPText:
    def __init__(self, text, position=None, rotation=0):
        self.text = text
        self.position = position
        self.rotation = rotation

    def __repr__(self):
        return f'<Text "{self.text}" @{self.position}>'

class LPComposite:
    def __init__(self, gridsize=None, gridposition=None):
        self.gridsize = gridsize
        self.gridposition = gridposition

    def __repr__(self):
        return f'<LPComposite: {self.gridsize} @{self.gridposition}>'

class LPWhitespacePrefix:
    def __init__(self, text):
        self.text = text

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
