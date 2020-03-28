#!/usr/bin/python3
'''
Class for intermediate layout objects
'''

from utils import get_image_size, DEFAULT_SIZE

class Meme:
    def __init__(self, image: str = None, size=None, fillcolor='white'):
        self.image = image
        self.size = size or get_image_size(image) or DEFAULT_SIZE
        self.fillcolor = fillcolor

    def __repr__(self):
        return f'<Meme: {self.image} ({self.size[0]}x{self.size[1]})>'

class Text:
    def __init__(self, text, position=None, rotation=0):
        self.text = text
        self.position = position
        self.rotation = rotation

    def __repr__(self):
        return f'<Text "{self.text}" @{self.position}>'

class Composite:
    pass

class WhitespacePrefix:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return f'<WP: {self.text}>'
