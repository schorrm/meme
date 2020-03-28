#!/usr/bin/python3

from utils import *
from render.format import FormatManager

import os
import hashlib
from contextlib import suppress
import warnings

from PIL import Image

class Meme:
    def __init__(self, image_handle: str, size: Coordinates, fillcolor: str = '#fff', mode: str = "resize"):
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

        self.load_config(file_path)
        self.max_row = 1
    
    def load_config(self, file_path):
        config_path = file_path + CONFIG_EXT
        if os.path.exists(config_path):
            cfg = open(config_path)
        else:
            cfg = DEFAULT_TEXT_FIELD_CFG

        # TODO: Implement. something like
        # for json_obj in json.load(cfg): self.fields[json_obj.name] = json_obj.bbox
        pass

    def update_max_row(self, tag: LPOutput):
        if type(tag.position) == str:
            if tag.position[1].is_digit():
                row = int(tag.position[1:])
                self.max_row = max(self.max_row, row)

    def build_lookup_table(self):
        right = self.fields["RIGHT"]
        left = self.fields["LEFT"]
        for i in range(1, max_row + 1):
            self.fields[f'r{i}'] = (initial_height, right[1], end_height, right[3])
            self.fields[f'l{i}'] = (initial_height, left[1], end_height, left[3])

    def resolve_text_args(self, tag: LPOutput):
        # TODO: implement, or rename get_position
        args = {}

        if type(tag.position) == str:
            if tag.position[-1] == "%":
                # TODO: implement percentage-based text position
                pass
            else:
                args["position"] = self.fields[tag.position]

        return args

class DrawingManager:
    def __init__(self):
        self.format_manager = FormatManager()

    def DrawMeme(self, image_handle: str, size: Coordinates, mode: str, fillColor: str, scoped_tags={}, child_tags=[]) -> Image:
        ''' Draw a meme '''
        self.format_manager.push_context(**scoped_tags)
        
        meme = Meme(image_handle, size)

        for tag in child_tags:
            if tag.type == TagType.TEXT:
                meme.update_max_row(tag)

        meme.build_lookup_table()

        for tag in child_tags:
            if tag.type == TagType.TEXT:
                args = meme.resolve_text_args(tag.data)
                self.DrawText(meme.image, **args)

            elif tag.type == TagType.POP:
                self.format_manager.pop_tag(**expand_tag(tag))

            else: # otherwise it's a formatting tag
                self.format_manager.update_context(tag)

        self.format_manager.pop_context()

        meme.end()

        return meme.img

    def DrawText(self, image, text, position, rotation):
        pass

