from render.format_types import Font, Alignment, Color
import warnings
from utils import TagType

# TODO: text style supported as 4th field on Font obj. How does text_style work?
# * is /TS:style/ tag only shorthand for /F:::style/?
# * is it toggle bitfield or overwrite?
# * what happens if calling /END:TS/ after /F/ or vice versa? (Do we need a 4th Style object?)
class FormatManager:
    class FormatContext:
        def __init__(self, def_font=Font(), def_align=None, def_color=None):
            self.fonts = [def_font]
            self.aligns = [def_align]
            self.colors = [def_color]

        @property
        def current_font(self):
            return self.fonts[-1]

        @property
        def current_align(self):
            return self.aligns[-1]

        @property
        def current_color(self):
            return self.colors[-1]

        @property
        def current_format(self):
            return (self.current_font, self.current_align, self.current_color)

        def F_tag(self, font):
            self.fonts.append(font.inherit_from(self.current_font))

        def AL_tag(self, align):
            self.aligns.append(align.inherit_from(self.current_align))

        def CL_tag(self, color):
            self.colors.append(color.inherit_from(self.current_color))

        def TS_tag(self, font):
            self.F_tag(font)

        def update_context(self, tag):
            # TODO: Actually define the tag type and how to access it / pull details out of it.
            if tag.type == TagType.FONT:
                self.F_tag(tag.data)
            elif tag.type == TagType.ALIGNMENT:
                self.AL_tag(tag.data)
            elif tag.type == TagType.COLOR:
                self.CL_tag(tag.data)
            elif tag.type == TagType.TEXTSTYLE:
                self.TS_tag(tag.data)
            elif tag.type == TagType.POP:
                warnings.warn("Got POP tag in update_context(). pop_tag() should be called explicitly", RuntimeWarning)
                self.pop_tag(tag)
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
            elif tag.data == 'TS':
                thing = self.fonts
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

    def scoped_F_tag(self, font_face, font_size, outline_size):
        """ Convenience function for a scoped font tag on a text block, to avoid needing to call push/get/pop """
        return Font(font_face, font_size, outline_size, None).inherit_from(self.current_font)

    def scoped_AL_tag(self, horizontal, vertical):
        """ Convenience function for a scoped alignment tag on a text block, to avoid needing to call push/get/pop """
        return Align(horizontal, vertical).inherit_from(self.current_align)

    def scoped_CL_tag(self, foreground, background, outline):
        """ Convenience function for a scoped color tag on a text block, to avoid needing to call push/get/pop """
        return Color(foreground, background, outline).inherit_from(self.current_color)

    def scoped_TS_tag(self, text_style):
        """ Convenience function for a scoped text style tag on a text block, to avoid needing to call push/get/pop """
        return Font(None, None, None, text_style).inherit_from(self.current_font)
