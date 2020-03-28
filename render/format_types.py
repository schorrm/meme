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

    def inherit_from(self, update_font):
        if self.outline_size == None:
            self.outline_size = update_font.outline_size
        self.font_size = self.font_size or update_font.font_size
        self.font_face = self.font_face or update_font.font_face

    def __repr__(self):
        return f'<{self.font_face} {self.font_size}, {self.outline_size}>'


class Alignment:
    def __init__(self, halign: str, valign: str):
        self.halign = halign
        self.valign = valign

    def inherit_from(self, update_alignment):
        self.halign = self.halign or update_alignment.halign
        self.valign = self.valign or update_alignment.valign

    def __repr__(self):
        return f'<Align {self.halign}, {self.valign}>'

class Color:
    def __init__(self, foreground: str = "black", background: str = None, outline: str = "white"):
        self.foreground = foreground
        self.background = background
        self.outline = outline

    def inherit_from(self, update_color):
        self.foreground = self.foreground or update_color.foreground
        self.background = self.background or update_color.background
        self.outline = self.outline or update_color.outline

    def __repr__(self):
        return f'<Color: FG={self.foreground}, BG={self.background}, OL={self.outline}>'

