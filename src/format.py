from .format_types import Font, Alignment, Color
import warnings
from .defines import TagType

# TODO: text style supported as 4th field on Font obj. How does text_style work?
# * is /TS:style/ tag only shorthand for /F:::style/?
# * is it toggle bitfield or overwrite?
# * what happens if calling /END:TS/ after /F/ or vice versa? (Do we need a 4th Style object?)


class FormatManager:
    class FormatContext:
        def __init__(self, def_font=Font(), def_align=Alignment(), def_color=Color()):
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
            if tag.type == TagType.FONT:
                self.F_tag(tag)
            elif tag.type == TagType.ALIGNMENT:
                self.AL_tag(tag)
            elif tag.type == TagType.COLOR:
                self.CL_tag(tag)
            elif tag.type == TagType.TEXTSTYLE:
                self.TS_tag(tag)
            elif tag.type == TagType.POP:
                warnings.warn(
                    "Got POP tag in update_context(). pop_tag() should be called explicitly", SyntaxWarning)
                self.pop_tag(tag)
            else:
                # TODO: Usefuller error messages. Own error type(s)?
                raise RuntimeError("Got bad tag type")

        def pop_tag(self, tag):
            """ Handles a pop tag """
            match tag:
                case TagType.FONT | TagType.TEXTSTYLE:
                    target_array = self.fonts
                case TagType.ALIGNMENT:
                    target_array = self.aligns
                case TagType.COLOR:
                    target_array = self.colors
                case _:
                    raise RuntimeError("Invalid pop tag data")

            if len(target_array) > 1:
                target_array.pop()
            else:
                raise SyntaxError("Can't pop default formatting specifier")

        def _flatten(self):
            self.fonts = [self.current_font]
            self.aligns = [self.current_align]
            self.colors = [self.current_color]

    @property
    def _current_context(self):
        return self.contexts[-1]

    def __init__(self):
        self.contexts = [FormatManager.FormatContext()]

    def push_context(self, scoped_tags):
        """ Adds a new context (Container or Meme) to the stack """
        self.contexts.append(FormatManager.FormatContext(self.current_font,
                                                         self.current_align,
                                                         self.current_color))
        for tag in scoped_tags:
            self.update_context(tag)

        self._current_context._flatten()

    def pop_context(self):
        """ Remove the current context when the Meme/Container ends """
        self.contexts.pop()

    def __getattr__(self, attr):
        return getattr(self._current_context, attr)

    def scoped_context(self, scoped_tags):
        """ Convenience function for handling scoped format tags, use instead of push/update/pop """
        self.push_context(scoped_tags)
        context = self._current_context
        self.pop_context()
        return context
