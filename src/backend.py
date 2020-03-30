#!/usr/bin/python3

from typing import Union
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
        rleft, rtop, rright, rbottom = self.fields["RIGHT"]
        lleft, ltop, lright, lbottom = self.fields["LEFT"]

        rdelta = (rtop - rbottom) / self.max_row # this may need to be //
        ldelta = (ltop - lbottom) / self.max_row # this may need to be //

        rbaseline = rtop
        lbaseline = ltop

        for i in range(1, self.max_row + 1):
            self.fields[f'r{i}'] = (rleft, rbaseline, rright, rbaseline + rdelta)
            self.fields[f'l{i}'] = (lleft, lbaseline, lright, lbaseline + ldelta)
            rbaseline += rdelta
            lbaseline += ldelta

    def resolve_position(self, position: Union[str, BBox]):
        # I'm assuming here that it's going to come in as a tuple when not named?
        if type(position) == str: # this should be a named position, find appropriate tuple
            try:
                position =  self.fields[position]
            except:
                raise KeyError("Me looking for your named position directive like")
    
        directions = list(position)
        for direction, max_value in zip(directions, [self.width, self.height, self.width, self.height]): # l t r b
            if direction.endswith("%"): # TODO: NOTE: This may not come as percent, 
                                        #             we need to watch this, given that % is reserved
                direction = (int(direction[:-1]) / 100) * max_value # convert all % to pixel values

        return tuple(directions)

    def add_text(self, text: str, font: PIL.ImageFont, bbox: BBox, rotation: float):
        ''' Draw text to a location '''
        # TODO: Figure out division of labor with DrawingManager.DrawText
        pass


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
                self.DrawText(meme, **args)

            elif tag.type == TagType.POP:
                self.format_manager.pop_tag(**expand_tag(tag))

            else: # otherwise it's a formatting tag
                self.format_manager.update_context(tag)

        self.format_manager.pop_context()

        return meme.image

    def DrawText(self, meme, text, position, rotation):
        # TODO: handle outline
        bbox = meme.resolve_position(position)
        width = bbox[2] - bbox[0] # r - l
        height = bbox[3] - bbox[1] # b - t
        final_text, final_font = optimize_text(text, self.format_manager.current_font, width, height)

        # TODO: find division of labor with Meme.add_text
        # * Define temporary image with correct BG
        # * render text to said image, with correct halign
        # * redraw text with correct color
        # * rotate temporary image
        # * calculate paste position for proper valign
        # * paste to actual image

