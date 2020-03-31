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
    _default_order = DEFAULT_FIELD_ORDER

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
        self.field_order = Meme._default_order
        if os.path.exists(config_path):
            with open (config_path) as f:
                field_data = json.load(f)
                self.fields.update(field_data["namedFields"])
                if field_data.get("defaultOrder"):
                    self.field_order = field_data["defaultOrder"]
                
        self.active_mode = 'general'
        self.mode_generators = {
            # self.fields only has str indices, so if self.field_order[idx] is a tuple we get None and return the tuple
            "general": lambda idx: self.fields.get(self.field_order[idx]) or self.field_order[idx],
            "r": lambda idx: self.fields[f"r{idx}"],
            "l": lambda idx: self.fields[f"l{idx}"]
        }
        self.mode_indices = {
            "general": 0,
            "r": 1,
            "l": 1
        }

    @property
    def active_index(self):
        return self.mode_indices[self.active_mode]

    def update_index(self, last=None):
        """ steps the active index, if a last parameter is given, it sets the counter to there first"""
        if last is not None:
            self.mode_indices[self.active_mode] = last
        else:
            self.mode_indices[self.active_mode] += 1

    @property
    def next_position(self) -> BBox:
        return self.mode_generators[self.active_mode](self.active_index)

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

    def resolve_position(self, position: Union[str, BBox, int, None]):
        if type(position) == int: # general position index -> tuple/named position
            self.active_mode = "general"
            self.update_index(position)
            position = self.next_position
        elif type(position) == str: # this should be a named position, find appropriate tuple
            # allow auto position to work after l/r explicit position
            if position[0] in "lr" and position[1].is_digit(): # NOTE: lexer-parser MUST use "left" and "right"
                self.active_mode = position[0]
                self.update_index(int(position[1:]))
            elif position in self.field_order: # allow implicit following of general order
                self.active_mode = "general"
                self.update_index(self.field_order.index(position))
            try:
                # Not using next_position to explicitly catch bad names
                position = self.fields[position]
            except:
                raise KeyError("Me looking for your named position directive like")
        elif not position: # auto case
            position = self.next_position
        
        # self.next_position is guaranteed to be the current position at this point
        # so here we prep for the next call
        self.update_index()
        
        # handle percentages
        directions = list(position)
        for direction, max_value in zip(directions, [self.width, self.height, self.width, self.height]): # l t r b
            if direction.endswith("%"): # TODO: NOTE: This may not come as percent, 
                                        #             we need to watch this, given that % is reserved
                direction = round((int(direction[:-1]) / 100) * max_value) # convert all % to pixel values

        return tuple(directions)

    def add_text(self, text_img: Image, position: BBox):
        ''' Draw text to a location '''
        self.image.paste(text_img, position)


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

        context = get_current_format_context() # how does this work? don't care, resolve scoped tags with current context

        final_text, final_font, (final_width, final_height) = optimize_text(text, context.font, width, height)
        if context.current_color.background:
            temp = Image.new("RGBA", (width, height), color=context.current_color.background)
        else:
            temp = Image.new("RGBA", (width, height), color=(0,0,0,0))

        valign = context.current_align.valign or "top"
        halign = context.current_align.halign or "center"
        if valign == "top":
            x = 0
        elif valign == "bottom":
            x = height - final_height
        else:
            x = (height-final_height)/2

        if halign == "left":
            y = 0
        elif halign == "right":
            y = width - final_width
        else:
            y = (width - final_width)/2

        draw = ImageDraw.Draw(temp)
        draw.multiline_text((x, y), final_text, fill=context.current_color.foreground, font=final_font,
                            align=halign, stroke_width=context.current_font.outline_size,
                            stroke_fill=context.current_color.outline)
        # if rotation != 0: # rotation is a fucking mess, v2.0
        #     temp = temp.rotate(rotation, expand=True)
        #     new_width, new_height = temp.getsize()
        #     x = bbox[0] + (width - new_width)/2
        #     y = bbox[1] + (height - new_height)/2
        # else:
        #     x, y, _, _ = bbox
        meme.add_text(temp, bbox) # paste to actual image

