#!/usr/bin/python3

from utils import *
from render.format import FormatManager

import os
import hashlib
from contextlib import suppress
import warnings

from PIL import Image

class DrawingManager:
    def __init__(self):
        self.format_manager = FormatManager()

    def InitImage(self, image_handle: str, size: Coordinates, fillcolor: str = '#fff', mode: str = "resize"):
        ''' Create an Image to start drawing text on. '''
        if not image_handle:
            return Image.new('RGB', size, fillcolor)

        file_path = resolve_file_path(image_handle)
        image = Image.open(file_path)
        if size and image.size != size:
            
            if mode == "resize":
                if image.size[0]/size[0] != image.size[1]/size[1]:
                    warnings.warn(f"Resizing image from {image.size} to {size} doesn't preserve aspect ratio", RuntimeWarning)
                image = image.resize(size)
            elif mode == "crop":
                image = image.crop(get_bbox(smaller=size, larger=image))
            elif mode == "fill":
                image = Image.new('RGB', size, fillcolor).paste(image, get_bbox(smaller=image, larger=size))
            else:
                raise RuntimeError("Bad Mode")

        return image


    def DrawMeme(self, image_handle: str, size: Coordinates, scoped_tags={}, child_tags=[]) -> Image:
        ''' Draw a meme '''
        
        self.format_manager.push_context(**scoped_tags)
        
        curr_img = self.InitImage(image_handle, size)

        for tag in child_tags:
            if tag.type == TagType.TEXT:
                self.DrawText(tag, curr_img)

            elif tag.type == TagType.POP:
                self.format_manager.pop_tag(**expand_tag(tag))

            else: # otherwise it's a formatting tag
                self.format_manager.update_context(tag)

        self.format_manager.pop_context()

        return curr_img
