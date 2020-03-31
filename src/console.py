#!/usr/bin/python3

import argparse

from lark import Lark
from transform_parse_tree import ConvertParseTree
from stack_manager import StackManager
import os
from PIL import Image

with open('grammar_enforcing.lark') as f:
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

args = parser.parse_args()

if not args.string or args.loadfile:
    raise RuntimeError("Y u no meme")

memestr = args.string
if not memestr:
    with open(args.loadfile) as f:
        memestr = f.read()

img = memestr_to_img(memestr)
img.save(os.path.join(os.getcwd(), args.outputfile))
