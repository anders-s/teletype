# coding=utf-8

from __future__ import print_function

from ..codes import escape_sequences
from ..exceptions import TeletypeQuitException
from ..io import (
    erase_screen,
    get_key,
    move_cursor,
    show_cursor,
    style_format,
    style_print,
)
from .config import get_glyph


class SelectMany:
    def __init__(self, choices, header="", **options):
        self._line = 0
        self._selected_lines = set()
        unique_choices = set()
        self.choices = [
            choice
            for choice in choices
            if choice not in unique_choices
            and (unique_choices.add(choice) or True)
        ]
        self.header = header
        self.erase_screen = options.get("erase_screen") is True

    def prompt(self):
        g_arrow = get_glyph("arrow")
        g_unselected = get_glyph("unselected")
        if not self.choices:
            return
        show_cursor(False)
        if self.erase_screen:
            erase_screen()
        if self.header:
            style_print(self.header, style="bold")
        for i, choice in enumerate(self.choices):
            print("%s%s %s " % (" " if i else g_arrow, g_unselected, choice))
        move_cursor(rows=-1 * i - 1)
        while True:
            key = get_key()
            if key in {"up", "k"}:
                self._move_line(-1)
            elif key in {"down", "j"}:
                self._move_line(1)
            elif key in {"ctrl-c", "ctrl-d", "ctrl-z"} | escape_sequences:
                show_cursor(True)
                raise TeletypeQuitException
            elif key == "space":
                self._select_line()
            elif key == "lf":
                break
        if self.erase_screen:
            erase_screen()
        else:
            move_cursor(rows=len(self.choices) - self._line + 1)
        show_cursor(True)
        return self.selected

    def _move_line(self, distance):
        g_arrow = get_glyph("arrow")
        offset = (self._line + distance) % len(self.choices) - self._line
        if offset == 0:
            return
        self._line += offset
        print(" ", end="")
        move_cursor(rows=offset, cols=-1)
        print("%s" % g_arrow, end="")
        move_cursor(cols=-1)

    def _select_line(self):
        self._selected_lines ^= {self._line}
        move_cursor(cols=1)
        glyph = get_glyph(
            "selected" if self._line in self._selected_lines else "unselected"
        )
        print(glyph, end="")
        move_cursor(cols=-2)

    @property
    def selected(self):
        return [
            self.choices[line % len(self.choices)]
            for line in self._selected_lines
        ]
