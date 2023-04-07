#!/usr/bin/python3

from typing import Union
from .utils import *
from .defines import *
from .format import FormatManager

import os
import hashlib
from contextlib import suppress
import warnings
import json

from bidi.algorithm import get_display

from .layout_objects import LPComposite, LPMeme, LPText, LPWhitespacePrefix
from .format_types import Font, Color, Alignment, Time

from PIL import Image, ImageDraw


class Meme:
    _default_config = DEFAULT_FIELD_CFG
    _default_order = DEFAULT_FIELD_ORDER

    def __init__(self, image_handle: str, size: Coordinates, fillcolor: str = 'white', mode: str = "resize"):
        ''' Create an Image to start drawing text on. '''
        if not image_handle:
            image = Image.new('RGBA', size, fillcolor)
            file_path = ''
        else:
            file_path = resolve_file_path(image_handle)
            image = Image.open(file_path)
            self.is_gif = True
            if not file_path.endswith('.gif'):
                self.is_gif = False
                image = image.convert('RGBA')
                if size[0] and size[1] and image.size != size:

                    if mode == "resize":
                        if image.size[0]/size[0] != image.size[1]/size[1]:
                            warnings.warn(
                                f"Resizing image from {image.size} to {size} doesn't preserve aspect ratio", RuntimeWarning)
                        image = image.resize(size)
                    elif mode == "crop":
                        image = image.crop(
                            get_bbox(smaller=size, larger=image))
                    elif mode == "fill":
                        image = Image.new('RGBA', size, fillcolor).paste(
                            image, get_bbox(smaller=image, larger=size))
                    else:
                        raise RuntimeError("Bad Mode")

        self.image = image
        self.load_config(file_path)
        self.max_row = 1
        self.deferred_texts_and_times = []
        # self.draw = ImageDraw.Draw(self.image, mode=self.draw_mode)

    @property
    def width(self):
        return self.image.size[0]

    @property
    def height(self):
        return self.image.size[1]

    def _convert_percentage_values(self, coords: BBox) -> BBox:
        axes = [self.width, self.height, self.width, self.height]
        coords = list(coords)
        for i, (direction, max_value) in enumerate(zip(coords, axes)):  # l t r b
            # TODO: NOTE: This may not come as percent,
            if type(direction) == str and direction.endswith("%"):
                # we need to watch this, given that % is reserved
                # convert all % to pixel values
                coords[i] = round((int(direction[:-1]) / 100) * max_value)
            elif type(direction) == str:
                coords[i] = int(direction)

        return tuple(coords)

    def load_config(self, file_path: str):
        self.fields = Meme._default_config.copy()
        config_path = file_path + CONFIG_EXT
        self.field_order = Meme._default_order
        self.default_format = []
        if os.path.exists(config_path):
            with open(config_path) as f:
                field_data = json.load(f)
                self.fields.update(field_data.get("namedFields", {}))
                if field_data.get("defaultOrder"):
                    self.field_order = field_data["defaultOrder"]
                format_data = field_data.get("format_data")
                if format_data is not None:
                    def _make_dict(name, args):
                        d = {arg: None for arg in args}
                        d.update(format_data.get(name, {}))
                        return d

                    self.default_format = [Font(**_make_dict("font", FONT_DATA)),
                                           Alignment(
                                               **_make_dict("alignment", ALIGN_DATA)),
                                           Color(**_make_dict("color", COLOR_DATA))]
        # this is defined here so that its a super untouchable reserved thingy
        self.fields["all"] = ("0%", "0%", "100%", "100%")

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
        do_update = True
        position = tag.position
        if position == None:
            # Update always done by fallthrough, do_update just stops general->(r|l)n derailing
            if self.active_mode == "general":
                position = self.active_index  # fallthrough to int case
            else:
                position = f'{self.active_mode}{self.active_index}'

        # Following the default order
        if type(position) == int:
            self.active_mode = "general"
            self.update_index(position)
            # fallthrough if general order contains (r|l)n directives
            position = self.field_order[self.active_index]
            do_update = False

        # (r|l)n
        if type(position) == str:
            if position[0] in "rl" and position[1].isdigit():
                row = int(position[1:])
                self.max_row = max(self.max_row, row)
                if do_update:  # only override the current stuff if this isn't a fallthrough from the general ordering
                    self.active_mode = position[0]
                    self.update_index(row)

        self.update_index()  # advance to next position

    def build_lookup_table(self):
        # make fields safe
        for k, v in self.fields.items():
            self.fields[k] = self._convert_percentage_values(v)

        rleft, rtop, rright, rbottom = self.fields["RIGHT"]
        lleft, ltop, lright, lbottom = self.fields["LEFT"]

        rdelta = (rbottom - rtop) / self.max_row  # this may need to be //
        ldelta = (lbottom - ltop) / self.max_row  # this may need to be //

        rbaseline = rtop
        lbaseline = ltop

        for i in range(1, self.max_row + 1):
            self.fields[f'r{i}'] = (rleft, round(
                rbaseline), rright, round(rbaseline + rdelta))
            self.fields[f'l{i}'] = (lleft, round(
                lbaseline), lright, round(lbaseline + ldelta))
            rbaseline += rdelta
            lbaseline += ldelta

        # Reset mode_indices for wet run
        self.mode_indices = {"general": 0, "r": 1, "l": 1}

    def resolve_position(self, position: Union[str, BBox, int, None]) -> BBox:
        if type(position) == int:  # general position index -> tuple/named position
            self.active_mode = "general"
            self.update_index(position)
            position = self.next_position
        elif type(position) == str:  # this should be a named position, find appropriate tuple
            # allow auto position to work after l/r explicit position
            # NOTE: lexer-parser MUST use "left" and "right"
            if position[0] in "lr" and position[1].isdigit():
                self.active_mode = position[0]
                self.update_index(int(position[1:]))
            elif position in self.field_order:  # allow implicit following of general order
                self.active_mode = "general"
                self.update_index(self.field_order.index(position))
            try:
                # Not using next_position to explicitly catch bad names
                position = self.fields[position]
            except:
                raise KeyError(
                    "Me looking for your named position directive like")
        elif not position:  # auto case
            position = self.next_position

        # self.next_position is guaranteed to be the current position at this point
        # so here we prep for the next call
        self.update_index()

        # handle percentages
        return self._convert_percentage_values(position)

    def add_text(self, text_img: Image, position: Coordinates):
        ''' Draw text to a location '''
        self.image.alpha_composite(text_img, position)

    def add_text_to_gif(self, text_img: Image, position: Coordinates, frames: tuple[int, int]):
        self.deferred_texts_and_times.append([text_img, position, frames])

    def generate_gif(self) -> list[Image]:
        assert self.is_gif

        frames = []

        for frame_num in range(self.image.n_frames):
            self.image.seek(frame_num)
            new_frame = Image.new('RGBA', self.image.size)
            new_frame.paste(self.image)
            for text, position, (minframe, maxframe) in self.deferred_texts_and_times:
                if minframe <= frame_num <= maxframe:
                    new_frame.alpha_composite(text, position)
            frames.append(new_frame)

        return frames


class DrawingManager:
    def __init__(self):
        self.format_manager = FormatManager()
        self.frame: int = 0
        self.drawing_mode: str = 'RGBA'
        self.is_gif: bool = False

    def DrawTextMeme(self, tag: LPMeme, scoped_tags=[], child_tags=[]) -> Image:
        self.format_manager.push_context(scoped_tags)

        text_tags = [tag for tag in child_tags if tag.type == TagType.TEXT]
        if len(text_tags) != 1:
            raise SyntaxError("Undefined Text Thingy")
        text = text_tags[0]
        context = self.format_manager.scoped_context(text.scoped_tags)
        _, _, (_, new_height) = optimize_text(text.tag.text,
                                              context.current_font, tag.size[0])  # no max height, as high as we need

        tag.size = (tag.size[0], new_height + OFFSET_WHITESPACE)

        meme = Meme(tag.image, tag.size, tag.fillcolor, tag.mode)
        self.DrawText(meme, text)

        # for tag_or_scope in child_tags:
        #     if tag_or_scope.type == TagType.TEXT:
        #     else:
        #         raise SyntaxError("How did you even get a format tag here?")
        self.format_manager.pop_context()
        return meme.image

    def DrawMeme(self, tag: LPMeme, scoped_tags=[], child_tags=[]) -> Image:
        ''' Draw a meme '''
        meme = Meme(tag.image, tag.size, tag.fillcolor, tag.mode)

        self.format_manager.push_context(meme.default_format + scoped_tags)

        for tag in child_tags:
            if tag.type == TagType.TEXT:
                meme.update_max_row(tag.tag)

        meme.build_lookup_table()

        if meme.is_gif and meme.image.is_animated:
            self.is_gif = True
            # self.drawing_mode = 'RGB'
            total_time = meme.image.n_frames * meme.image.info['duration']
            last_frame = meme.image.n_frames - 1

            def seconds_to_frame(seconds: float) -> int:
                seconds = min(seconds, total_time)
                return round((seconds / total_time) * last_frame)

            def process_time_directive(time: Time) -> Time:
                if time.seconds:
                    start, end = time.seconds
                    start_frame = seconds_to_frame(start) if start else 0
                    end_frame = seconds_to_frame(end) if end else last_frame
                    return Time(frames=(start_frame, end_frame))

                else:
                    start, end = time.frames
                    start_frame = start or 0
                    end_frame = end or 0
                    return Time(frames=(start_frame, end_frame))

            for tag_or_scope in child_tags:
                match tag_or_scope.type:
                    case TagType.TIME:
                        self.format_manager.update_context(
                            process_time_directive(tag_or_scope))
                    case TagType.POP:
                        self.format_manager.pop_tag(tag_or_scope.target)
                    case TagType.TEXT:
                        self.DrawText(meme, tag_or_scope)
                    case _:
                        self.format_manager.update_context(tag_or_scope)

            frames = meme.generate_gif()
            base = frames[0]
            base.info = meme.image.info
            base.save('_tmp_gen.gif', save_all=True,
                      append_images=frames[1:])
            im = Image.open('_tmp_gen.gif')
            return im

        else:
            for tag_or_scope in child_tags:
                if tag_or_scope.type == TagType.TEXT:
                    self.DrawText(meme, tag_or_scope)

                elif tag_or_scope.type == TagType.POP:
                    self.format_manager.pop_tag(tag_or_scope.target)

                else:  # otherwise it's a formatting tag
                    self.format_manager.update_context(tag_or_scope)

        self.format_manager.pop_context()

        return meme.image

    def DrawText(self, meme, scope):
        text = scope.tag.text
        position = scope.tag.position
        scope.tag.resolved_position = scope.tag.resolved_position or meme.resolve_position(
            position)
        # rotation = scope.tag.rotation

        bbox = scope.tag.resolved_position

        width = bbox[2] - bbox[0]  # r - l
        height = bbox[3] - bbox[1]  # if meme.has_height else None # b - t

        # how does this work? don't care, resolve scoped tags with current context
        context = self.format_manager.scoped_context(scope.scoped_tags)

        final_text, final_font, (final_width, final_height) = optimize_text(
            text, context.current_font, width, height)
        final_text = get_display(final_text)
        if height is None:
            height = final_height
        if context.current_color.background:
            temp = Image.new(self.drawing_mode, (width, height),
                             color=context.current_color.background)
        else:
            temp = Image.new(self.drawing_mode,
                             (width, height), color=(0, 0, 0, 0))

        valign = context.current_align.valign or "top"
        halign = context.current_align.halign or "center"
        if valign == "top":
            y = 0
        elif valign == "bottom":
            y = height - final_height
        else:
            y = (height-final_height)/2

        if halign == "left":
            x = 0
        elif halign == "right":
            x = width - final_width
        else:
            x = (width - final_width)/2

        draw = ImageDraw.Draw(temp, mode=self.drawing_mode)
        draw.text((x, y), final_text, fill=context.current_color.foreground, font=final_font,
                  align=halign, stroke_width=context.current_font.outline_size,
                  stroke_fill=context.current_color.outline)
        # if rotation != 0: # rotation is a fucking mess, v2.0
        #     temp = temp.rotate(rotation, expand=True)
        #     new_width, new_height = temp.getsize()
        #     x = bbox[0] + (width - new_width)/2
        #     y = bbox[1] + (height - new_height)/2
        # else:
        #     x, y, _, _ = bbox
        if self.is_gif:
            meme.add_text_to_gif(
                temp, bbox[:2], self.format_manager._current_context.current_time.frames)
        else:
            meme.add_text(temp, bbox[:2])  # paste to actual image
