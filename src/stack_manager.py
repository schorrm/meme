#!/usr/bin/python3

from typing import List
import warnings
from .format_types import Alignment, Color, Font, TextStyle
from .layout_objects import LPComposite, LPMeme, LPText, LPWhitespacePrefix, Pop
from .backend import DrawingManager
from .utils import *
from .defines import TagType, WP_DEFAULT_FONT, WP_DEFAULT_FONTSIZE, WP_DEFAULT_OL_SIZE
from PIL import Image, ImageDraw
from math import ceil


class Scope:
    def __init__(self, tag, scoped_tags=None):
        self.tag = tag
        self.scoped_tags = scoped_tags or []
        self.children = []
        self.type = tag.type

    def __repr__(self):
        s = f'<Scope {self.tag} ({self.scoped_tags})>\n'
        for child in self.children:
            for line in str(child).splitlines():
                s += f'\t{line}\n'
        s += '</Scope>'
        return s


class StackManager:
    def __init__(self):
        self.scopes = []
        self._last_scope = None
        self.drawing_manager = DrawingManager()

    @property
    def current_scope_tag(self):
        if len(self.scopes):
            return self.scopes[-1].tag
        return None

    @property
    def current_scope(self):
        if len(self.scopes) == 0:
            raise SyntaxError("Cannot access nonexistent scope")
        #     warnings.warn("Trying to access non-existent scope. Attempting recovery", SyntaxWarning)
        #     recovery_scope = Scope(tag=LPComposite(gridsize=(1, None)))
        #     recovery_scope.children.append(self._last_scope)
        #     self.scopes.append(recovery_scope)
        return self.scopes[-1]

    def pop_meme(self):
        self._last_scope = self.scopes.pop()
        if type(self._last_scope.tag) == LPComposite:
            warnings.warn("Popped composite as meme/wp", RuntimeWarning)
        self.current_scope.children.append(self._last_scope)

    def pop_composite(self):
        while type(self.current_scope_tag) == LPMeme:
            self.pop_meme()
        self._last_scope = self.scopes.pop()
        if len(self.scopes) > 0:
            self.current_scope.children.append(self._last_scope)
        # else:
            # self.current_scope  # this invokes the recovery code in the current_scope property

    def add_scope(self, tag, scoped_tags):
        # All
        if type(self.current_scope_tag) == LPMeme:
            self.pop_meme()
        self.scopes.append(Scope(tag, scoped_tags))

    def parse(self, tag_list: List[List]) -> List:
        if type(tag_list[0][0]) != LPComposite:
            self.scopes.append(Scope(tag=LPComposite(gridsize=(1, None))))

        self.lookaheads = 0
        for tag, *scoped_tags in tag_list:
            match tag:
                case LPText():
                    self.current_scope.children.append(
                        Scope(tag, scoped_tags))
                case LPWhitespacePrefix():
                    # TODO: Figure out dependencies between auto and lookahead and also actually program them in somewhere (here vs backend?)
                    self.add_scope(LPMeme(image=None, size=(
                        "lookahead", None), fillcolor='white'), list())
                    self.current_scope.children.append(Scope(LPText(tag.text, position='all'), [Alignment("left", "top"), Font(
                        WP_DEFAULT_FONT, WP_DEFAULT_FONTSIZE, WP_DEFAULT_OL_SIZE), *scoped_tags]))
                case LPMeme() | LPComposite():
                    self.add_scope(tag, scoped_tags)
                case Pop(target=TagType.MEME):
                    self.pop_meme()
                case Pop(target=TagType.COMPOSITE):
                    self.pop_composite()
                case _:
                    self.current_scope.children.append(tag)

        # implictly popping the meme caused non-existant scope errors
        if self.current_scope_tag == TagType.MEME:
            self.pop_meme()

        while len(self.scopes) > 1:
            self.pop_composite()

        return self._last_scope

    def DrawStack(self, scope: Scope) -> Image:
        images = []
        deferred = []
        self.drawing_manager.format_manager.push_context(scope.scoped_tags)
        for child in scope.children:
            if child.type == TagType.COMPOSITE:
                images.append(self.DrawStack(child))
            elif child.type == TagType.MEME:
                if child.tag.size[0] == "lookahead":
                    deferred.append(len(images))
                    images.append(child)
                else:
                    image = self.drawing_manager.DrawMeme(
                        child.tag, child.scoped_tags, child.children)
                    images.append(image)
            elif child.type.is_format:
                self.drawing_manager.format_manager.update_context(child)

            elif child.type == TagType.POP and child.target.is_format:
                self.drawing_manager.format_manager.pop_tag(child.target)

        for idx in reversed(deferred):
            # we iterate in reverse order to deal with the edge case of
            # having consecutive lookaheads, so that we construct the
            # second one first, preventing the first one from winding
            # up with a size that's still ("lookahead", <something>)
            child = images[idx]
            # tuple doesn't support assignment
            child.tag.size = (images[idx+1].size[0], child.tag.size[1])
            images[idx] = self.drawing_manager.DrawTextMeme(
                child.tag, child.scoped_tags, child.children)

        self.drawing_manager.format_manager.pop_context()

        cols, rows = scope.tag.gridsize
        if rows is None:
            if cols is None:
                raise SyntaxError("Only one of width and height can be auto")
            rows = ceil(len(images)/cols)
        elif cols is None:
            cols = ceil(len(images)/rows)

        def idx2pair(idx):
            return idx % cols, idx//cols

        def pair2idx(c, r):
            return c+(r*cols)
        next_gridposition = 0

        grid = [[None]*rows for _ in range(cols)]
        for i in range(len(images)):
            c, r = scope.children[i].tag.gridposition or idx2pair(
                next_gridposition)
            next_gridposition = pair2idx(c, r)+1
            grid[c][r] = {"image": images[i], "tag": scope.children[i].tag}

        col_widths = [
            max(map(lambda r: grid[c][r]["image"].size[0], range(rows))) for c in range(cols)]
        row_heights = [
            max(map(lambda c: grid[c][r]["image"].size[1], range(cols))) for r in range(rows)]

        positions = [[None]*rows for _ in range(cols)]

        for r in range(rows):
            for c in range(cols):
                positions[c][r] = (sum(col_widths[:c]), sum(row_heights[:r]))

        base_image = Image.new(
            "RGB", (sum(col_widths), sum(row_heights)), color='white')
        draw = ImageDraw.Draw(base_image, mode='RGBA')

        for c in range(cols):
            for r in range(rows):
                # Fill entire grid cell
                x, y = positions[c][r]
                tag = grid[c][r]["tag"]
                fill = 'white'
                if type(tag) == LPMeme and tag.fillcolor:
                    fill = tag.fillcolor
                draw.rectangle(
                    ((x, y), (x+col_widths[c], y+row_heights[r])), fill)
                base_image.paste(grid[c][r]["image"], positions[c][r])

        return base_image
