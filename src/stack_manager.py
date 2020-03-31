#!/usr/bin/python3

from typing import List

from render.format_types import Alignment, Color, Font, TextStyle
from layout_objects import LPComposite, LPMeme, LPText, LPWhitespacePrefix, Pop
from utils import *

def is_layout_obj(obj) -> bool:
    return type(obj) in [LPMeme, LPComposite, LPText, LPWhitespacePrefix]

class Scope:
    def __init__(self, tag, scoped_tags=[]):
        self.tag = tag
        self.scoped_tags = scoped_tags
        self.children = []

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

    @property
    def current_scope(self):
        return self.scopes[-1]

    def parse(self, tag_list: List[List]) -> List:

        if type(tag_list[0][0]) != LPComposite:
            self.scopes.append(Scope(tag=LPComposite(gridsize=(1,None))))
            

        for tag, *scoped_tags in tag_list:
            if is_layout_obj(tag): # create new scope for layout object
                if type(tag) == LPText:
                    self.current_scope.children.append(Scope(tag, scoped_tags))
                elif type(tag) == LPWhitespacePrefix: #TODO IDK
                    self.scopes.append(Scope(tag, scoped_tags))
                elif type(tag) == LPMeme:
                    print('huh')
                    print(self.scopes)
                    print(self.current_scope)
                    if type(self.current_scope.tag) == LPMeme:
                        meme = self.scopes.children.pop()
                        self.current_scope.children.append(meme)
                    self.scopes.append(Scope(tag, scoped_tags))
            else:
                self.current_scope.children.append(tag)

        else:
            buf = []
            while type(self.current_scope) == LPMeme:
                buf.append(self.scopes.children.pop())
            self.current_scope.children += buf


        