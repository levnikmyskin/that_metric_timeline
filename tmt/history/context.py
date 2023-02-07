from __future__ import annotations
from tmt.storage.schema import Entry, Result
from tmt.storage.json_db import DbManager
from uuid import uuid4
from datetime import datetime
from contextvars import ContextVar
from tmt.configs.parser import Configs
from typing import Optional, Any, Callable
from tmt.exceptions import DuplicatedNameError
from tmt.utils.duplicates import DuplicateStrategy, DuplicatePolicy
import os
import sys
import pickle
import warnings

context_manager: ContextVar[ContextManager] = ContextVar('context_manager', default=None)


class ContextManager:
    def __init__(self, name: str, config_path: Optional[str] = None, duplicate_strategy=DuplicateStrategy(), description=""):
        if config_path:
            self.config = Configs.from_config(config_path)
        else:
            self.config = Configs.default_config()
        self.entry = Entry(
            id=str(uuid4()),
            name=name,
            description=description,
            args=' '.join(sys.argv),
            date_created=int(datetime.now().timestamp()),
            local_results_path=self.config.results_path,
        )
        self.duplicate_strat = duplicate_strategy
        self.parent = DbManager(self.config.json_db_path).get_entries_by_name(name)
        if self.parent:
            if self.duplicate_strat.policy is DuplicatePolicy.DONT_ALLOW:
                raise DuplicatedNameError(f'one (or more) entry with name {name} already exists. Set '
                                          f'`duplicate_strategy` or change name (recommended)')
            elif self.duplicate_strat.policy is DuplicatePolicy.AS_SUB_ENTRY:
                if len(self.parent) > 1:
                    parent_id = self.duplicate_strat.parent_id
                    parent_dict = {e.id: e for e in self.parent}
                    if not self.duplicate_strat.parent_id or self.duplicate_strat.parent_id not in parent_dict:
                        parent = sorted(self.parent, key=lambda e: e.date_created, reverse=True)[0]
                        warnings.warn(f'{len(self.parent)} entries already exist with this name and a '
                                      f'valid DuplicateStrategy.parent_id was not specified. I will use {parent.short_str()} as '
                                      f'the parent entry. See documentation for DuplicateStrategy.')
                        parent_id = parent.id
                    self.parent = parent_dict[parent_id]
                else:
                    self.parent = self.parent[0]
                self.parent.other_runs.append(self.entry)
            elif self.duplicate_strat.policy is DuplicatePolicy.AS_NEW_ENTRY:
                self.parent = None
        self.snap_manager = self.config.init_snapshot_manager(self.entry.id)
        self.entry.local_snapshot_path = self.snap_manager.snapshot_dest
        os.makedirs(self.get_save_path(), exist_ok=True)
        self.last_saved_counter = 0

    @property
    def root_entry(self) -> Entry:
        if self.parent and self.duplicate_strat.policy is DuplicatePolicy.AS_SUB_ENTRY:
            return self.parent
        return self.entry

    def save(self, obj: Any, name: str, allow_exist=False, extension='.pkl',
             custom_save: Optional[Callable[[Any, str], Optional[str]]] = None) -> str:
        path = self.get_save_path_with_name(name)
        if os.path.exists(path):
            if not allow_exist:
                raise DuplicatedNameError(f'{self.get_save_path_with_name(name)} already exists and `allow_exist` is '
                                          f'False. Specify another name to save this object')
            else:
                path = self.increment_last_saved_path(name)
        path += extension
        if custom_save is not None:
            custom_path = custom_save(obj, path)
            path = custom_path if custom_path is not None else path
        else:
            with open(path, 'wb') as f:
                pickle.dump(obj, f)
        self.entry.results.append(Result(self.entry.id, name, path))
        return path

    def get_save_path_with_name(self, name: str):
        return os.path.join(self.get_save_path(), name)

    def get_save_path(self):
        return os.path.join(self.entry.local_results_path, self.entry.id)

    def increment_last_saved_path(self, name: str):
        self.last_saved_counter += 1
        return os.path.join(self.get_save_path(), f'{name}_{self.last_saved_counter}')
