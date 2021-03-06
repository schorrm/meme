#!/usr/bin/python3

from lark import Lark

from transform_parse_tree import ConvertParseTree

from stack_manager import StackManager

import pprint

import os

from PIL import Image

with open('grammar_enforcing.lark') as f:
    t = f.read()
l = Lark(t, parser='lalr')

strings = [
    "/M/",
    "/M/T:~~/",
    "/M/T:~//",
    "/M/T:~~~~/T:Too_Many_Tildes/",
    "/M/T:~~~~~~~~~~/",
    "/M/T:~nNewline_Start/",
    "/M:doge/T:Much_Block_Parsing/",
    "/M:doge/T:Much_escaping~/_foo/",
    "/M:doge/T:Much~_escap~~ing~/_foo/",
    "/M:doge/F:Helvetica:20/T:More_escaping~~/T:HARD/",
    "/M:doge/F:Helvetica:20/T:Several~~Literal~~Tildes/",
    "/M/T:~~~~/T:Too_Many_Tildes/",
    "/M/T:~~~n/T:Tilde_ThenNewline/",
    "/M/T:~~~n~~/T:Tilde_ThenNewline/",
    "/M/T:~:/T:Colon/",
    "/M/T:~;/T:Semicolon/",
    "/M/T:Foo;F:Bar/T:Semicolon/",
    "/M:drake;F:Helvetica:20/T:WYSIWYG:r1/T:Handwritten Markup:r2/",
    "/M:drake:640x480;F:Helvetica:20/T:WYSIWYG:r1/T:Handwritten Markup:r2/",
    "/M:drake:640x480;F:Helvetica:20;TS:bui/T:WYSIWYG:r1/T:Handwritten Markup:r2/",
    "/M:.localmeme.png/T:Local_text_support/CL:alicewhite:#fff:#f0f0f0/",
    "/M:.localmeme.png/T:Local_text_support/CL:alicewhite::#f0f0f0/",
    "/M/AL::b/AL:c:c/",
    "/M:doge:640x420::1,3;F:Helvetica:20/AL::b/F::22/AL:c:c/T:SomeTextHere/AL:c/AL::c/CL:aliceblue:#fff:#000/CL:::tomato/",
    "/WP:MFW_when/M:doge;F:arial:12/T:SomeoneIsDoging:bottom/",
    "/WP:MFW_when/M:doge;F:arial:12/F/CL/AL/T:SomeoneIsDoging:bottom/",
    "/M:drake;F:arial/T:WYSIWYG:r1/T:Handwritten Markup:r2/",
]

transformer = ConvertParseTree()

for s in strings:
    print(s)
    # print(l.parse(s).pretty())
    pprint.pprint(transformer.transform(l.parse(s)))
    print()

tl = transformer.transform(l.parse(s))
manager = StackManager()
processed_tree = manager.parse(tl)

for scope in manager.scopes:
    print (scope)

print(len(manager.scopes))

img = manager.DrawStack(processed_tree)
import numpy as np

# print(np.asarray(img))

img.save(os.path.join(os.getcwd(), "your_meme.png"))
