from __future__ import annotations
from tmt.storage.schema import Entry, Result
from tmt.storage.json_db import DbManager
from uuid import uuid4
from datetime import datetime
from contextvars import ContextVar
from tmt.configs.parser import Configs
from typing import Optional, Any
from tmt.exceptions import DuplicatedNameError
import os
import sys
import pickle


context_manager: ContextVar[ContextManager] = ContextVar('context_manager', default=None)


class ContextManager:
    def __init__(self, name: str, config_path: Optional[str] = None, allow_duplicate_names=False):
        if config_path:
            self.config = Configs.from_config(config_path)
        else:
            self.config = Configs.default_config()
        if DbManager(self.config.json_db_path).get_entries_by_name(name) and not allow_duplicate_names:
            raise DuplicatedNameError(f'one (or more) entry with name {name} already exists. Set `allow_duplicate_names=True` or change name (recommended)')
        self.entry = Entry(
            id=str(uuid4()), 
            name=name, 
            args=' '.join(sys.argv), 
            date_created=int(datetime.now().timestamp()), 
            local_results_path=self.config.results_path,
            )
        self.snap_manager = self.config.init_snapshot_manager(self.entry.id)
        self.entry.local_snapshot_path = self.snap_manager.snapshot_dest
        os.makedirs(self.get_save_path(), exist_ok=True)
        self.last_saved_counter = 0

    def save(self, obj: Any, name: str, allow_exist=False, extension='.pkl') -> str:
        path = self.get_save_path_with_name(name)
        if os.path.exists(path):
            if not allow_exist:
                raise DuplicatedNameError(f'{self.get_save_path_with_name(name)} already exists and `allow_exist` is False. Specify another name to save this object')
            else:
                path = self.increment_last_saved_path(name)
        path += extension
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
