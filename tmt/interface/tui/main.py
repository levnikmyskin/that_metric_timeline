from prompt_toolkit import Application
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.containers import Window, HSplit, WindowAlign
from prompt_toolkit.layout.controls import FormattedTextControl, DummyControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.widgets import Frame
from tmt.interface.tui.search import SearchLayout, SearchBy
from tmt.interface.tui.entry_display import EntryDisplay
from tmt.interface.tui.base import BaseApp, FocusableText
from tmt.storage.schema import Entry
from typing import Optional
from functools import partial

kb = KeyBindings()

@kb.add('c-q')
def exit_(event):
    event.app.exit()


class MainApp(BaseApp):
    # TODO serve a proper "window_too_small" window
    def __init__(self, config_path: Optional[str] = None):
        self.search_layout = SearchLayout(back_handler=self.main_window, entry_select_handler=self.entry_display, config_path=config_path)
        self.main_container = HSplit([
            Frame(
                title='That Metric Timeline (TMT)', 
                body=HSplit([
                    Window(content=FormattedTextControl(text='This is the Terminal User Interface (TUI) of That Metric Timeline library. You can look for recorded experiments and see their details\nChoose an option from below:'), height=3),
                    HSplit([
                        FocusableText('Search experiment by name', align=WindowAlign.CENTER, ext_height=False, handler=self.search_by_name),
                        FocusableText('Search experiment by ID', align=WindowAlign.CENTER, ext_height=False, handler=self.search_by_id),
                        FocusableText('Search experiment by date', align=WindowAlign.CENTER, ext_height=False, handler=self.search_by_date)], padding=1),
                    Window(content=DummyControl(), height=6)
                    ])),
            self._bottom_toolbar()
        ], padding=3)
        self.layout = Layout(self.main_container)
        kb.add("tab")(focus_next)
        kb.add("down")(focus_next)
        kb.add("s-tab")(focus_previous)
        kb.add("up")(focus_previous)

        self.search_by = None
        self.app = Application(full_screen=True, layout=self.layout, key_bindings=kb)

    def main_window(self):
        self.app.layout = self.layout

    def search_by_name(self, clear=True):
        self.search_by = SearchBy.NAME
        layout = self.search_layout.search_by_name_layout(clear)
        self.app.layout = Layout(layout, focused_element=layout)
    
    def search_by_id(self, clear=True):
        self.search_by = SearchBy.ID
        layout = self.search_layout.search_by_id_layout(clear)
        self.app.layout = Layout(layout, focused_element=layout)

    def search_by_date(self, clear=True):
        pass

    def entry_display(self, entry: Entry):
        if self.search_by is SearchBy.NAME:
            back_handler = partial(self.search_by_name, False)
        elif self.search_by is SearchBy.ID:
            back_handler = partial(self.search_by_id, False)
        elif self.search_by is SearchBy.DATE:
            back_handler = partial(self.search_by_date, False)
        else:
            back_handler = self.main_window
        layout = EntryDisplay(entry, back_handler=back_handler).get_layout()
        self.app.layout = Layout(layout, focused_element=layout)

    def run(self):
        self.app.run()


if __name__ == '__main__':
    import sys
    MainApp(sys.argv[1]).run()