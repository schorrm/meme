#!/usr/bin/python3

from typing import Tuple

from utils import *

from render.format import FormatManager

Coordinates = Tuple[int, int]



class DrawingManager:

    def __init__(self):
        self.format_manager = FormatManager()

    def DrawMeme(self, image: str, size: Coordinates, scoped_tags={}, child_tags=[]) -> Image:
        ''' Draw a meme '''
        
        self.format_manager.push_context(**scoped_tags)
        
        curr_img = InitImage(image, size)

        for tag in child_tags:
            if tag.type == TagType.TEXT:
                self.DrawText(tag, curr_img)

            elif tag.type == TagType.POP:
                self.format_manager.pop_tag(tag)

            else: # otherwise it's a formatting tag
                self.format_manager.update_context(tag)

        self.format_manager.pop_context()

        return curr_img


        