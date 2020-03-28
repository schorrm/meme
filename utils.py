#!/usr/bin/python3

import os
import glob

from typing import Tuple, List
from enum import Enum, auto, unique

from collections import ChainMap


DEFAULT_SIZE = (640, 480)

def get_image_size(filename: str) -> Tuple[int, int]:
    pass

@unique
class TagType(Enum):
    # TODO: enumerate our types
    FONT = auto()
    ALIGNMENT = auto()
    COLOR = auto()
    TEXT = auto()
    POP = auto()

    @property
    def is_format(self):
        return self in [TagType.FONT, TagType.ALIGNMENT, TagType.COLOR]

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
