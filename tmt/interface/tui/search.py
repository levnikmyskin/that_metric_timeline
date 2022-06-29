from prompt_toolkit.layout.containers import Window, HSplit, VSplit, to_container, HorizontalAlign, WindowAlign
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.widgets import Frame, Button, Label, Shadow
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.utils import Event
from typing import Optional, Callable, Iterable
from tmt.configs.parser import Configs
from tmt.storage.json_db import DbManager
from tmt.storage.schema import Entry
from tmt.interface.tui.base import BaseApp, FocusableText, date_formatter
from functools import partial
from enum import Enum, auto


class SearchBy(Enum):
    NAME = auto()
    ID = auto()
    DATE = auto()


class SearchLayout(BaseApp):

    def __init__(self, back_handler: Callable, entry_select_handler: Callable, config_path: Optional[str] = None):
        if config_path:
            self.config = Configs.from_config(config_path)
        else:
            self.config = Configs.from_default_path_or_default_config()
        self.db = DbManager(self.config.json_db_path, read_only=True)
        self.results_box = HSplit([Label(text='No results...')])
        self.search_label = Label(text='', dont_extend_width=True)
        self.search_text = Buffer(multiline=False)
        self.search_box = VSplit([self.search_label, Window(BufferControl(self.search_text))], padding=2)
        self.back_handler = back_handler
        self.entry_select_handler = entry_select_handler

    def search_by_name_layout(self, clear):
        self.search_label.text = 'Search name:'
        self.search_text.on_text_changed = Event(self.search_text, self.search_by_name)
        if clear:
            self.__clear_results()
            self.__clear_search_text()
        return self.__search_layout()

    def search_by_id_layout(self, clear):
        self.search_label.text = 'Search ID (exact match):'
        self.search_text.on_text_changed = Event(self.search_text, self.search_by_id)
        if clear:
            self.__clear_results()
            self.__clear_search_text()
        return self.__search_layout()

    def search_by_name(self, buffer: Buffer):
        try:
            entries = self.db.get_entries_by_name_regex(buffer.text)
        except:
            entries = []

        if buffer.text == '' or len(entries) == 0:
            self.__clear_results()
            return
        self._show_results(entries)

    def search_by_id(self, buffer: Buffer):
        entry = self.db.get_entry_by_id(buffer.text)
        if buffer.text == '' or entry is None:
            self.__clear_results()
            return
        self._show_results((entry,))
    
    def search_by_date(self, buffer: Buffer):
        pass
        
    def _show_results(self, entries: Iterable[Entry]):
        self.results_box.children = []
        ids = HSplit([Label(text='ID')])
        names = HSplit([Label(text='Name')])
        dates = HSplit([Label(text='Date created')])
        self.results_box.children.append(VSplit([ids, names, dates]))
        for entry in entries:
            ids.children.append(to_container(FocusableText(entry.id, handler=partial(self.entry_select_handler, entry))))
            names.children.append(to_container(Label(text=entry.name)))
            dates.children.append(to_container(Label(text=date_formatter(entry.date_created))))


    def _bottom_toolbar(self):
        toolbar = super()._bottom_toolbar()
        toolbar.children.insert(0, to_container(Button('back', handler=self.back_handler)))
        return toolbar

    def __clear_results(self):
        self.results_box.children = [to_container(Label(text='No results...'))]

    def __clear_search_text(self):
        self.search_text.reset()

    def __search_layout(self):
        return HSplit([Frame(body=HSplit([self.search_box, Shadow(Frame(ScrollablePane(self.results_box)))], padding=1)), self._bottom_toolbar()], padding=5)

