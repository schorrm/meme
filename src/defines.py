#!/usr/bin/python3

import os.path
from enum import Enum, auto, unique
 
# We were worried about too much in utils, so we now have a separation.
# This file is meant for all the various global defaults and settings.

DEFAULT_SIZE = (640, 480)
DEFAULT_FONT_SIZE = 100

OFFSET_WHITESPACE = 5

SML_DIR = os.path.join(os.path.expanduser("~"), '.local', 'lib', 'meme', 'sml')
LIB_DIR = os.path.join(os.path.expanduser("~"), '.local', 'lib', 'meme', 'libs')

DEFAULT_FIELD_CFG = { "RIGHT"  : ("50%",  "0%", "100%", "100%"), # r1..rn
                      "LEFT"   : ( "0%",  "0%",  "50%", "100%"), # l1..ln
                      "top"    : ( "0%",  "0%", "100%",  "20%"),
                      "bottom" : ( "0%", "80%", "100%", "100%"),
                      "center" : ( "0%", "40%", "100%",  "60%"),
                      "rtop"   : ("50%",  "0%", "100%",  "20%"),
                      "rbottom": ("50%", "80%", "100%", "100%"),
                      "rcenter": ("50%", "40%", "100%",  "60%"),
                      "ltop"   : ( "0%",  "0%",  "50%",  "20%"),
                      "lbottom": ( "0%", "80%",  "50%", "100%"),
                      "lcenter": ( "0%", "40%",  "50%",  "60%")
                    }
DEFAULT_FIELD_ORDER = ("top", "bottom", "center", "rtop", "rbottom", "rcenter", "ltop", "lbottom", "lcenter")

CONFIG_EXT = '.memeconfig' # Would still be neat to support embedding this stuff in JPEG EXIF fields / PNG Text chunks. -> later version

# Default formatting for WP to meme
WP_DEFAULT_FONT = 'arial'
WP_DEFAULT_FONTSIZE = 60
WP_DEFAULT_OL_SIZE = 0



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
    WHITESPACE = auto()


    @property
    def is_format(self):
        return self in [TagType.FONT, TagType.ALIGNMENT, TagType.COLOR, TagType.TEXTSTYLE]
