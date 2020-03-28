#!/usr/bin/python3

import os
import glob

from typing import Tuple, List
from enum import Enum, auto, unique

from collections import ChainMap

from typing import Tuple
Coordinates = Tuple[int, int]
BBox = Tuple[int, int, int, int]

## IMAGE UTILS

DEFAULT_SIZE = (640, 480)

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

# TODO: come up with some bullshit to make this platform-independent
SML_DIR = '/usr/local/lib/meme/sml'
LIB_DIR = '/usr/local/lib/meme/lib'


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
