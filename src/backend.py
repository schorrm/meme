#!/usr/bin/python3

from utils import *
from render.format import FormatManager

import os
import hashlib
from contextlib import suppress
import warnings
import json

from layout_objects import LPComposite, LPMeme, LPText, LPWhitespacePrefix

from PIL import Image, ImageDraw

class Meme:
    _default_config = DEFAULT_FIELD_CFG

    def __init__(self, image_handle: str, size: Coordinates, fillcolor: str = '#fff', mode: str = "resize"):
        ''' Create an Image to start drawing text on. '''
        if not image_handle:
            image = Image.new('RGB', size, fillcolor)
        else:
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

        self.image = image
        self.load_config(file_path)
        self.max_row = 1
        self.draw = ImageDraw.Draw(self.image)

    @property
    def width(self):
        return self.image.size[0]

    @property
    def height(self):
        return self.image.size[1]
    
    def load_config(self, file_path: str):
        self.fields = Meme._default_config.copy()
        config_path = file_path + CONFIG_EXT
        if os.path.exists(config_path):
            with open (config_path) as f:
                self.fields.update(json.load(f))

    def update_max_row(self, tag: LPText):
        if type(tag.position) == str:
            if tag.position[1].is_digit():
                row = int(tag.position[1:])
                self.max_row = max(self.max_row, row)

    def build_lookup_table(self):
        rtop, rright, rbottom, rleft = self.fields["RIGHT"]
        ltop, lright, lbottom, lleft = self.fields["LEFT"]

        rdelta = (rtop - rbottom) / self.max_row # this may need to be //
        ldelta = (ltop - lbottom) / self.max_row # this may need to be //

        rbaseline = rtop
        lbaseline = ltop

        for i in range(1, self.max_row + 1):
            self.fields[f'r{i}'] = (rbaseline, rright, rbaseline + rdelta, rleft)
            self.fields[f'l{i}'] = (lbaseline, lright, lbaseline + ldelta, lleft)
            rbaseline += rdelta
            lbaseline += ldelta

    def resolve_text_args(self, tag: LPText):
        # TODO: implement, or rename get_position
        args = {}

        # I'm assuming here that it's going to come in as a tuple when not named?
        if type(tag.position) == str: # this should be a named position, find appropriate tuple
            try:
                args["position"] = self.fields[tag.position]
            except:
                raise KeyError("Me looking for your named position directive like")
        else:
            directions = list(tag.position)
            for direction, max_value in zip(directions, [self.height, self.width, self.height, self.width]): # t r b l
                if direction.endswith("%"): # TODO: NOTE: This may not come as percent, 
                    # we need to watch this, given that % is reserved
                    direction = (int(direction[:-1]) / 100) * max_value # convert all % to pixel values

            args["position"] = tuple(directions)

        return args

    def add_text(self, tag: LPText, location: BBox):
        ''' Draw text to a location '''


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

