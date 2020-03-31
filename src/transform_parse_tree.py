#!/usr/bin/python3

from lark import Lark, Transformer

from utils import unpack, unpack3, list2dict
from defines import TagType

from format_types import Font, Alignment, Color
from layout_objects import LPMeme, LPText, LPComposite, LPWhitespacePrefix, Pop

import copy

def _extract_monic(tree):
    if tree:
        return tree[0].value
    return None


class ConvertParseTree(Transformer):
    def start(self, tree):
        return tree

    def block(self, subtree):
        return subtree

    def fontname(self, fontname):
        if fontname:
            return fontname[0].value
        return None

    def fontsize(self, fontsize):
        return int(fontsize)

    def font(self, subtree):
        if not subtree:
            return Pop(TagType.FONT)
        font_name, font_size, outline_size = unpack3(subtree)
        return Font(font_name, font_size, outline_size)

    def halign(self, halign):
        return _extract_monic(halign)

    def valign(self, valign):
        return _extract_monic(valign)

    def align(self, alignments):
        if not alignments:
            return Pop(TagType.ALIGNMENT)
        halign, valign = unpack(alignments)
        return Alignment(halign, valign)

    def colorarg(self, color):
        return _extract_monic(color)

    def colorblock(self, colors):
        if not colors:
            return Pop(TagType.COLOR)
        return Color(*colors)

    def imagehandle(self, image):
        return {'image': _extract_monic(image)}

    def size(self, coords):
        x, y = coords
        return {'size': (int(x), int(y))}

    def fillcolor(self, color):
        return {'color': _extract_monic(color)}

    def gridposition(self, coords):
        x, y = coords
        return {'position': (int(x), int(y))}

    # Layout Blocks:
    def memeblock(self, tree):
        tree = list2dict(tree)
        # position = tree.get('position')
        # if position:
        #     tree.pop('position')
        return LPMeme(**tree)

    def text(self, token):
        return {'text': _extract_monic(token)}

    def endcomposite(self, token):
        return Pop(TagType.COMPOSITE)

    def position(self, position):
        return {'position': _extract_monic(position)}

    def rotation(self, rotation):
        return {'rotation': _extract_monic(rotation)}

    def textblock(self, tree):
        return LPText(**list2dict(tree))

    def whitespaceprefix(self, text):
        return LPWhitespacePrefix(**text[0])
