#!/usr/bin/python3

from typing import Tuple

from utils import *

from render.format import FormatManager

Coordinates = Tuple[int, int]

import os
import hashlib
from contextlib import suppress

from PIL import Image as ImageFile, ImageFont, ImageDraw, ImageFilter

class DrawingManager:
    def __init__(self):
        self.format_manager = FormatManager()

    def InitImage(self, image_handle: str, size: Coordinates, fillcolor: str = '#fff'):
        ''' Create an Image to start drawing text on. '''
        if not image_handle:
            return Image.new('RGB', size, fillcolor)

        file_path = resolve_file_path(image_handle)


    def DrawMeme(self, image_handle: str, size: Coordinates, scoped_tags={}, child_tags=[]) -> Image:
        ''' Draw a meme '''
        
        self.format_manager.push_context(**scoped_tags)
        
        curr_img = InitImage(image_handle, size)

        for tag in child_tags:
            if tag.type == TagType.TEXT:
                self.DrawText(tag, curr_img)

            elif tag.type == TagType.POP:
                self.format_manager.pop_tag(tag)

            else: # otherwise it's a formatting tag
                self.format_manager.update_context(tag)

        self.format_manager.pop_context()

        return curr_img


        