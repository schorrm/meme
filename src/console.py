#!/usr/bin/python3

import argparse

from lark import Lark
from .transform_parse_tree import ConvertParseTree
from .stack_manager import StackManager
from .utils import get_fml_memes, install_fml
import os
from PIL import Image, PngImagePlugin

def main():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'grammar_enforcing.lark')

    with open(filename) as f:
        t = f.read()
    l = Lark(t, parser='lalr')

    def memestr_to_img(memestr: str):
        transformer = ConvertParseTree()
        tl = transformer.transform(l.parse(memestr))
        manager = StackManager()
        processed_tree = manager.parse(tl)
        img = manager.DrawStack(processed_tree)
        return img

    parser = argparse.ArgumentParser("Standard Meme Compiler: v0.1")

    parser.add_argument('-s', '--string', help="Create from string")
    parser.add_argument('-f', '--loadfile', help="Load Standard Meme Representation from file")
    parser.add_argument('-o', '--outputfile', default="default.meme.png", help="Output filename")
    parser.add_argument('-e', '--extractinfo', help="Extract meme representation from a meme")
    parser.add_argument('-l', '--listfml', action="store_true", help="List available FML memes")
    parser.add_argument('--getfml', action="store_true", help="Install the FML (Foundational Meme Library). Requires git.")

    args = parser.parse_args()

    if args.getfml:
        install_fml()
        exit(0)

    if args.listfml:
        for file in get_fml_memes():
            print(file)
        exit(0)

    if args.extractinfo:
        img = Image.open(args.extractinfo)
        data = img.info.get('memesource')
        if not data:
            print('Bad closed source meme')
            exit(1)
        else:
            print(data)
        exit(0)

    if not args.string or args.loadfile:
        raise RuntimeError("Y u no meme")

    memestr = args.string
    if not memestr:
        with open(args.loadfile) as f:
            memestr = f.read()


    # TODO: /M:dw-sign/T:Use with caution;F::75/T:Use with caution;F::20/
    # Write the source code to the output png image in the text chunk

    img = memestr_to_img(memestr)
    filename = os.path.join(os.getcwd(), args.outputfile)
    info = PngImagePlugin.PngInfo()
    info.add_text("memesource", memestr)

    img.save(filename, pnginfo=info)
