from filelock import FileLock
from tmt.storage.schema import Entry
from typing import List, Optional, Union, Iterable, Generator
from datetime import datetime
import os
import json
import warnings
import re


class DbManager:
    """
    Class to interact with the underlying json database. If `read_only` is `True`, all operations
    which add and/or modify the database won't be allowed.

    :param db_path: path to the json db file .
    :type db_path: str
    :param read_only: if `True` all writing access is denied, defaults to False.
    :type read_only: bool, optional
    """

    def __init__(self, db_path: str, read_only=False):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        if not os.path.exists(db_path):
            self.__init_db()
        self.lock = FileLock(f"{db_path}.lock")
        self.read_only = read_only

    def check_can_write(func):
        def inner(*args, **kwargs):
            if not args[0].read_only:
                return func(*args, **kwargs)
        return inner

    @check_can_write
    def add_new_entries(self, entries: List[Entry]):
        with self.lock:
            with open(self.db_path, 'r+') as f:
                db_data = json.load(f)
                for entry in entries:
                    if entry.id in {d['id'] for d in db_data['data']}:
                        warnings.warn(f'Entry with id {entry.id} already exists. This will not be overwritten.')
                        continue
                    db_data['data'].append(entry.to_dict())
                self.__write(db_data, f)

    @check_can_write
    def add_or_update_entry(self, entry: Entry):
        if self.get_entry_by_id(entry.id):
            self.update_entries([entry])
        else:
            self.add_new_entries([entry])

    @check_can_write
    def update_entries(self, entries: List[Entry]):
        with self.lock:
            with open(self.db_path, 'r+') as f:
                db_data = json.load(f)
                e_ids = {e.id: e for e in entries}
                for i, d in enumerate(db_data['data'].copy()):
                    if d['id'] in e_ids:
                        db_data['data'][i] = e_ids[d['id']].to_dict()
                self.__write(db_data, f)

    @check_can_write
    def delete_entry(self, entry: Entry) -> bool:
        with self.lock:
            with open(self.db_path, 'r+', encoding='utf-8') as f:
                db_data = json.load(f)
                for i, d in enumerate(db_data['data']):
                    if d['id'] == entry.id:
                        del db_data['data'][i]
                        self.__write(db_data, f)
                        return True
        return False

    @check_can_write
    def delete_all(self):
        self.__init_db()

    def get_entry_by_id(self, id: str) -> Optional[Entry]:
        with self.lock:
            with open(self.db_path, 'r') as f:
                db_data = json.load(f)['data']
                try:
                    return Entry.from_dict(next(filter(lambda e: e['id'] == id, db_data)))
                except StopIteration:
                    return None

    def get_entry_by_exact_name(self, name: str) -> Optional[Entry]:
        with self.lock:
            with open(self.db_path, 'r') as f:
                db_data = json.load(f)['data']
                entries = [e for e in db_data if e['name'] == name]
                if len(entries) > 1:
                    warnings.warn(f'Found {len(entries)} entries for name {name}. Returning the first one.')
                return Entry.from_dict(entries[0])

    def get_entries_by_name(self, name: str) -> List[Entry]:
        with self.lock:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            return list(map(Entry.from_dict, filter(lambda d: name in d['name'], db_data['data'])))

    def get_entries_by_name_regex(self, regex: str) -> List[Entry]:
        with self.lock:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            pattern = re.compile(regex)
            return list(map(Entry.from_dict, filter(lambda d: pattern.match(d['name']), db_data['data'])))

    def get_entries_between_dates(self, first: Union[datetime, int], second: Union[datetime, int]) -> List[Entry]:
        with self.lock:
            first, second = list(self.__convert_date_to_timestamp(first, second))
            with open(self.db_path, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            return list(map(Entry.from_dict, filter(lambda d: first <= d['timestamp'] <= second, db_data['data'])))

    def get_entries_greater_than_date(self, date: Union[datetime, int]) -> List[Entry]:
        with self.lock:
            timestamp = next(self.__convert_date_to_timestamp(date))
            with open(self.db_path, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            return list(map(Entry.from_dict, filter(lambda d: d['timestamp'] > timestamp, db_data['data'])))

    def get_entries_lower_than_date(self, date: Union[datetime, int]) -> List[Entry]:
        with self.lock:
            timestamp = next(self.__convert_date_to_timestamp(date))
            with open(self.db_path, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            return list(map(Entry.from_dict, filter(lambda d: d['timestamp'] < timestamp, db_data['data'])))

    def __convert_date_to_timestamp(*dates: Iterable[Union[datetime, int]]) -> Generator[int, None, None]:
        for date in dates:
            if type(date) is not int:
                date = date.timestamp()
            yield date

    def __init_db(self):
        with open(self.db_path, 'w') as f:
            # I don't like this "data" thing, but we used to use PysonDB...
            json.dump({"data": []}, f)

    def __write(self, data, f):
        f.seek(0)
        f.truncate()
        json.dump(data, f)
