class Font:
    def __init__(self, font_face='impact', font_size=14, outline_size=0):
        self.font_face = font_face
        self.font_size = font_size
        self.outline_size = outline_size
        self._cached_font = None
    
    @property
    def PIL_font(self):
        """ Return PIL.ImageFont instance """
        if not self._cached_font:
            pass
        return self._cached_font

    # TODO: Better name?
    def inherit(self, font_face=None, font_size=None, outline_size=None):
        return Font(font_face or self.font_face,
                    font_size or self.font_size,
                    outline_size or self.outline_size)


class Alignment:
    pass

class Color:
    pass