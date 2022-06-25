from prompt_toolkit.layout.containers import Window, HSplit, VSplit, to_container, Float, FloatContainer
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.widgets import Frame, Button, Box, Label, Shadow
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
from prompt_toolkit.formatted_text import HTML
from tmt.interface.tui.base import BaseApp, FocusableText, date_formatter
from tmt.storage.schema import Entry
from typing import Callable
from functools import partial
from prompt_toolkit.application.current import get_app


class EntryDisplay(BaseApp):
    def __init__(self, entry: Entry, back_handler: Callable):
        self.entry = entry
        self.back_handler = back_handler
        self.entry_disp = Frame(title=f'Experiment: {entry.name}', body=self.entry_layout())
        self.root_container = HSplit([self.entry_disp, self._bottom_toolbar()], padding=3)

    def get_layout(self):
        return self.root_container

    def entry_layout(self):
        keys = HSplit([
            Label(text='ID:', dont_extend_width=True),
            Label(text='Name:', dont_extend_width=True),
            Label(text='Args:', dont_extend_width=True),        
            Label(text='Date created:', dont_extend_width=True),
            Label(text='Metrics:', dont_extend_width=True),
            Label(text='Results path:', dont_extend_width=True),
            Label(text='Code snapshot path <enter to copy>:', dont_extend_width=True),
            Label(text='Date saved:', dont_extend_width=True)
        ], padding=1)
        ft_metric = FocusableText(text='<enter> to expand', handler=None)
        metric_float = FloatContainer(content=ft_metric, floats=[])
        ft_metric.set_handler(partial(self._on_metric_expand, metric_float))

        ft_results = FocusableText(text='<enter> to expand', handler=None)
        results_float = FloatContainer(content=ft_results, floats=[])
        ft_results.set_handler(partial(self._on_results_expand, results_float))
        vals = HSplit([
            Label(text=self.entry.id, dont_extend_width=True),
            Label(text=self.entry.name, dont_extend_width=True),
            Label(text=f'{self.entry.args or "NA"}', dont_extend_width=True),
            Label(text=date_formatter(float(self.entry.date_created)), dont_extend_width=True),
            metric_float,
            results_float,
            FocusableText(text=f'{self.entry.local_snapshot_path or "NA"}', handler=lambda: PyperclipClipboard().set_text(self.entry.local_snapshot_path)),
            Label(text=date_formatter(float(self.entry.date_saved)) if self.entry.date_saved else 'NA', dont_extend_width=True)
        ], padding=1)
        return Box(VSplit([keys, vals], padding=5))

    def _on_metric_expand(self, metric_float):
        metric_float.floats = [Float(Shadow(Frame(ScrollablePane(self._metric_layout(metric_float)))), top=0, width=20, height=10)]
        get_app().layout.focus(metric_float)

    def _on_metric_close(self, metric_float):
        metric_float.floats = []
        get_app().layout.focus(metric_float)

    def _on_results_expand(self, results_float):
        results_float.floats = [Float(Shadow(Frame(ScrollablePane(self._results_layout(results_float)))), left=0, width=40, height=10)]
        get_app().layout.focus(results_float)

    def _on_results_close(self, results_float):
        results_float.floats = []
        get_app().layout.focus(results_float)

    def _metric_layout(self, metric_float):
        keys = []
        vals = []
        if len(self.entry.metrics) == 0:
            keys.append(Label(text='No metrics found'))
        for metric in self.entry.metrics:
            keys.append(FocusableText(text=f'{metric.name.capitalize()}:'))
            vals.append(Window(content=FormattedTextControl(text=f'{metric.value:.5f}'), wrap_lines=True))
        return self._expandable_layout(keys, vals, metric_float, self._on_metric_close)

    def _results_layout(self, results_float):
        keys = []
        vals = []
        if len(self.entry.results) == 0:
            keys.append(Label(text='No results found'))
        keys.append(Label(text=HTML('<b>&lt;enter&gt; to copy</b>')))
        vals.append(Label(text=''))
        for res in self.entry.results:
            keys.append(FocusableText(text=f'{res.name.capitalize()} path:', handler=lambda: PyperclipClipboard().set_text(res.path)))
            vals.append(Window(content=FormattedTextControl(text=res.path), wrap_lines=True))
        return self._expandable_layout(keys, vals, results_float, self._on_results_close)

    def _expandable_layout(self, keys, vals, floating, handler):
        return HSplit([VSplit([HSplit(keys, padding=1), HSplit(vals, padding=1)], padding=1), FocusableText('<close>', handler=partial(handler, floating))], padding=3)

    def _bottom_toolbar(self):
        toolbar = super()._bottom_toolbar()
        toolbar.children.insert(0, to_container(Button('back', handler=self.back_handler)))
        return toolbar