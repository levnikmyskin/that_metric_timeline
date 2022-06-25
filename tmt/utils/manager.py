from tmt.storage.json_db import DbManager
from tmt.storage.schema import Entry, Metric
from tmt.configs.parser import Configs
from typing import Optional, Generator, Any, Tuple, List
from tmt.exceptions import EntryNotFound
import pickle


class TmtManager:

    def __init__(self, entry: Optional[Entry] = None, config: Optional[str] = None):
        if config is None:
            self.config = Configs.from_default_path_or_default_config()
        else:
            self.config = Configs.from_config(config)
        self.db = DbManager(self.config.json_db_path, read_only=True)
        self.entry = entry

    def set_entry_by_name(self, name: str) -> Entry:
        if (e := self.db.get_entry_by_exact_name(name)):
            self.entry = e
            return self.entry
        raise EntryNotFound(f'No entry (experiment) found for name {name}')

    def set_entry_by_id(self, id: str) -> Entry:
        if (e := self.db.get_entry_by_id(id)):
            self.entry = e
            return self.entry
        raise EntryNotFound(f'No entry (experiment) found for id {id}')

    def entry_not_none(func):
        def inner(*args, **kwargs):
            assert args[0].entry is not None, "This instance has not an `Entry` associated with it. Use one of the several `set_` methods"
            return func(*args, **kwargs)
        return inner
    
    @entry_not_none
    def load_results(self) -> Generator[Tuple[str, Any], None, None]:
        for result in self.entry.results:
            with open(result.path, 'rb') as f:
                yield result.name, pickle.load(f)

    @entry_not_none
    def results_paths(self) -> Generator[Tuple[str, str], None, None]:
        for result in self.entry.results:
            yield result.name, result.path

    @entry_not_none
    def get_metrics(self) -> List[Metric]:
        return self.entry.metrics

    @entry_not_none
    def code_snapshot_path(self) -> str:
        return self.entry.local_snapshot_path
