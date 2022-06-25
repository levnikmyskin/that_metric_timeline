from prompt_toolkit.layout.containers import Window, HSplit, VSplit, to_container, HorizontalAlign, WindowAlign
from prompt_toolkit.widgets import Label
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings
from typing import Optional, Callable
from datetime import datetime


class BaseApp:

    def _bottom_toolbar(self):
        return VSplit([Label(text='<ctrl>q: quit', style='fg:ansiblue', dont_extend_width=True), Label(text='<tab/arrows>: select', dont_extend_width=True, style='fg:ansiblue'), Label(text='<enter>: confirm', dont_extend_width=True, style='fg:ansiblue')], style="bg:ansiwhite", padding=3)


class FocusableText:

    def __init__(self, text: str, align: Optional[WindowAlign] = None, ext_width=True, ext_height=True, handler: Optional[Callable] = None):
        self.handler = handler
        self.control = FormattedTextControl(text=text, focusable=True, key_bindings=self.__get_key_bindings(), show_cursor=False)
        def style():
            if get_app().layout.has_focus(self):
                return 'bg:ansired'
            return 'class:label'
        self.window = Window(
            self.control,
            style=style,
            align=align,
            height=1,
            dont_extend_width=not ext_width,
            dont_extend_height=not ext_height,
        )

    def set_handler(self, handler: Callable):
        self.handler = handler
        self.control.key_bindings = self.__get_key_bindings()

    def __get_key_bindings(self):
        kb = KeyBindings()

        @kb.add(" ")
        @kb.add("enter")
        def _(event):
            if self.handler is not None:
                self.handler()

        return kb

    def __pt_container__(self):
        return self.window


def date_formatter(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime('%c')