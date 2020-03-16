from render.format_types import Font, Alignment, Color

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

        # def AL_tag(self, ...):
        #     pass

        # def CL_tag(self, ...):
        #     pass

        def update_context(self, tag):
            # TODO: Actually define the tag type and how to access it / pull details out of it.
            if tag.type == TagTypes.FONT:
                self.F_tag(**tag.data)
            elif tag.type == TagTypes.ALIGNMENT:
                self.AL_tag(**tag.data)
            elif tag.type == TagTypes.COLOR:
                self.CL_tag(**tag.data)
            else:
                # TODO: Usefuller error messages. Own error type(s)?
                raise RuntimeError("Got bad tag type")

        def pop_tag(self, tag):
            """ Handles a pop tag """
            # TODO: Better name for thing
            if tag.data == 'F':
                thing = self.fonts
            elif tag.data == 'AL':
                thing = self.aligns
            elif tag.data == 'CL':
                thing = self.colors
            else:
                raise RuntimeError("Invalid pop tag data")

            if len(thing) > 1:
                thing.pop()
            else:
                raise RuntimeError("Can't pop default formatting specifier")
        
    @property
    def _current_context(self):
        return self.contexts[-1]
    
    def __init__(self):
        self.contexts = []

    def push_context(self, f_tag=None, al_tag=None, cl_tag=None):
        """ Adds a new context (Container or Meme) to the stack """
        self.contexts.append(FormatManager.FormatContext(f_tag or self.current_font,
                                                         al_tag or self.current_align,
                                                         cl_tag or self.current_color))

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
