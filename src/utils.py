#!/usr/bin/python3

import os
import glob

from defines import *

from typing import Tuple, List, Union
from enum import Enum, auto, unique

from collections import ChainMap

from typing import Tuple
Coordinates = Tuple[int, int]
# 4 position coordinates each either a pixel number or a percentage string
BBox = Tuple[Union[int, str], Union[int, str], Union[int, str], Union[int, str]]

## IMAGE UTILS

def get_image_size(filename: str) -> Tuple[int, int]:
    pass

def get_bbox(smaller: Coordinates, larger: Coordinates) -> BBox:
    w_delta = (larger[0] - smaller[0])
    h_delta = (larger[1] - smaller[1])
    return (w_delta, h_delta, smaller[0]+w_delta, smaller[1]+h_delta)



@unique
class TagType(Enum):
    FONT = auto()
    ALIGNMENT = auto()
    COLOR = auto()
    TEXT = auto()
    TEXTSTYLE = auto()
    POP = auto()
    MEME = auto()
    COMPOSITE = auto()


    @property
    def is_format(self):
        return self in [TagType.FONT, TagType.ALIGNMENT, TagType.COLOR, TagType.TEXTSTYLE]

def unpack(l: List, nullvalue=None):
    """ Unpacks a tuple / list of 1 or 2 items to 2, safely """
    a, b, *_ = l + [nullvalue]
    return (a, b)


def unpack3(l: List, nullvalue=None):
    """ Unpacks a tuple / list of 1 or 2 items to 2, safely """
    a, b, c, *_ = l + [nullvalue, nullvalue, nullvalue]
    return (a, b, c)


def list2dict(l: List[dict]):
    return dict(ChainMap(*l))

def resolve_file_path(image_handle: str):
    # Resolve which directory we're looking at
    if image_handle.startswith('..'):
        workingdir = LIB_DIR
        image_handle = image_handle[2:]
    elif image_handle.startswith('.'):
        workingdir = os.getcwd()
        image_handle = image_handle[1:]
    else:
        workingdir = SML_DIR

    segments = image_handle.split('.')
    # TODO: ignore config files
    no_ex_pattern = os.path.join(workingdir, *segments) + '.*'
    last = segments.pop()
    ex_file = os.path.join(workingdir, *segments) + f'.{last}'
    if os.path.isfile(ex_file):
        return ex_file
    else:
        gresults = glob.glob(no_ex_pattern)
        if not gresults:
            raise RuntimeError("Me looking for your image like")  # TODO: Have good errors
        return gresults[0]

def _split(text):
    """Split a line of text into two similarly sized pieces.
    >>> _split("Hello, world!")
    ('Hello,', 'world!')
    >>> _split("This is a phrase that can be split.")
    ('This is a phrase', 'that can be split.')
    >>> _split("This_is_a_phrase_that_can_not_be_split.")
    ('This_is_a_phrase_that_can_not_be_split.',)
    """
    result = (text,)

    if len(text) >= 3 and ' ' in text[1:-1]:  # can split this string
        space_indices = [i for i in range(len(text)) if text[i] == ' ']
        space_proximities = [abs(i - len(text) // 2) for i in space_indices]
        for i, j in zip(space_proximities, space_indices):
            if i == min(space_proximities):
                result = (text[:j], text[j + 1:])
                break

    return result

def get_phrases(text, pil_font):
    lines = text.split('\n')
    return [lines, [pil_font.getsize(line) for line in lines]]

def split_longest(phrases, pil_font, max_width):
    lines, lengths = phrases
    longest = max(lengths)
    while longest > max_width:
        idx = lines.index(longest)
        split = _split(lines[idx])
        lines = lines[:idx] + split + lines[idx+1:]
        lengths = lengths[:idx] + [pil_font.getsize(line) for line in split] + lengths[idx+1:]
        longest = max(lengths)

    return [lines, lengths]

def optimize_text(text, font, max_width, max_height):
    pil_font = font.PIL_font
    font_size = font.font_size

    cur_text = text
    phrases = get_phrases(text, pil_font)

    success = False
    while not success:
        success = True
        
        text_size = pil_font.getsize_multiline(cur_text)
        if text_size[0] > max_width:
            phrases = split_long(phrases, pil_font, max_length)
            cur_text = '\n'.join(phrases[0])
        
        if text_size[1] > max_height:
            font_size -= 1
            if font_size == 0:
                raise RuntimeError("Too much text")
            pil_font = pil_font.font_variant(size=font_size)
            phrases = get_phrases(text, pil_font)
            cur_text = text

    return text, pil_font
