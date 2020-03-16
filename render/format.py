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

class FormatManager:
    class FormatContext:
        def __init__(self, def_font=Font(), def_align=None, def_color=None):
            self.fonts = [def_font]
            self.aligns = [def_align]
            self.colors = [def_color]

        @property
        def current_font(self):
            return self.fonts[-1]
            
        def F_tag(self, font_face, font_size, outline_size):
            self.fonts.append(self.current_font.inherit(font_face, font_size, outline_size))

        def pop_F(self):
            if len(self.font) > 1:
                self.fonts.pop()
            else:
                raise RuntimeError("Can't pop default font specifier")
        
    @property
    def _current_context(self):
        return self.contexts[-1]
    
    def __init__(self):
        self.contexts = []

    def push_context(self):
        """ Adds a new context (Container or Meme) to the stack """
        self.contexts.append(FormatManager.FormatContext(self.current_font, self.current_align, self.current_color))

    def pop_context(self):
        """ Remove the current context when the Meme/Container ends """
        self.contexts.pop()

    def __getattr__(self, attr):
        return getattr(self._current_context, attr)

    @property
    def current_font(self):
        """ Get current font """
        return self._current_context.current_font

    @property
    def current_align(self):
        """ Get current alignment """
        return self._current_context.current_align
    @property
    def current_color(self):
        """ Get current colors """
        return self._current_context.current_color

    def scoped_F_tag(self, font_face, font_size, outline_size):
        """ Convenience function for a scoped font tag on a text block, to avoid needing to call push/get/pop """
        return self.current_font.inherit(font_face, font_size, outline_size)

    def scoped_AL_tag(self, horizontal, vertical):
        """ Convenience function for a scoped alignment tag on a text block, to avoid needing to call push/get/pop """
        return self.current_align.inherit(horizontal, vertical)

    def scoped_CL_tag(self, foreground, background, outline):
        """ Convenience function for a scoped color tag on a text block, to avoid needing to call push/get/pop """
        return self.current_color.inherit(foreground, background, outline)
