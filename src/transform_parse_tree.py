#!/usr/bin/python3

from lark import Lark, Transformer

from utils import unpack, unpack3, list2dict
from defines import TagType

from format_types import Font, Alignment, Color
from layout_objects import LPMeme, LPText, LPComposite, LPWhitespacePrefix, Pop

ESCAPE_CHAR = '~'

escape_map = {
    'n': '\n',
    't': '\t'
}

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
        font_size = int(font_size) if font_size else None
        outline_size = int(outline_size) if outline_size else None
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
        return {'gridposition': (int(x), int(y))}

    def gridsize(self, coords):
        x, y = coords
        return {'gridsize': (int(x), int(y))}

    # Layout Blocks:
    def memeblock(self, tree):
        tree = list2dict(tree)
        # position = tree.get('position')
        # if position:
        #     tree.pop('position')
        return LPMeme(**tree)

    def text(self, token):
        text = _extract_monic(token)
        processed_text = ''
        escape = False
        for char in text:
            if escape: # previous char was escaped
                processed_text += escape_map.get(char, char)
                escape = False
            elif char == ESCAPE_CHAR:
                escape = True
            elif char == '_':
                escape = False
                processed_text += ' '
            else:
                escape = False
                processed_text += char

        return {'text': processed_text}

    def compositeblock(self, tree):
        return LPComposite(**list2dict(tree))

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
