#!/usr/bin/python3

from lark import Lark

import pprint

with open('grammar_enforcing.lark') as f:
    t = f.read()
l = Lark(t, parser='earley')

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
    "/M:doge/F:Helvetica:20pt/T:More_escaping~~/T:HARD/",
    "/M:doge/F:Helvetica:20pt/T:Several~~Literal~~Tildes/",
    "/M/T:~~~~/T:Too_Many_Tildes/",
    "/M/T:~~~n/T:Tilde_ThenNewline/",
    "/M/T:~~~n~~/T:Tilde_ThenNewline/",
    "/M/T:~:/T:Colon/",
    "/M/T:~;/T:Semicolon/",
    "/M/T:Foo;F:Bar/T:Semicolon/",
    "/M:drake;FF:Helvetica/T:WYSIWYG:r1/T:Handwritten Markup:r2/",
    "/M:drake;F:Helvetica:20pt/T:WYSIWYG:r1/T:Handwritten Markup:r2/",
    "/M:drake:640x480;F:Helvetica:20pt/T:WYSIWYG:r1/T:Handwritten Markup:r2/",
    "/M:drake:640x480;F:Helvetica:20pt;TS:bui/T:WYSIWYG:r1/T:Handwritten Markup:r2/",
    "/M:.localmeme.png/T:Local_text_support/",
]

for s in strings:
    print(s)
    print(l.parse(s).pretty())
    print()

pprint.pprint(l.parse(s))
