from pysondb import db
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

        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db = db.getDb(db_path)
        self.db._id_fieldname = '__json_id'
        self.read_only = read_only

    def check_can_write(func):
        def inner(*args, **kwargs):
            if not args[0].read_only:
                return func(*args, **kwargs)
        return inner

    @check_can_write
    def add_new_entries(self, entries: List[Entry]):
        self.db.addMany([e.to_dict() for e in entries])
    
    @check_can_write
    def delete_entry(self, entry: Entry) -> bool:
        with self.db.lock:
            with open(self.db.filename, 'r+', encoding='utf-8') as f:
                db_data = json.load(f)
                for i, d in enumerate(db_data['data']):
                    if d['id'] == entry.id:
                        del db_data['data'][i]
                        f.seek(0)
                        f.truncate()
                        json.dump(db_data, f)
                        return True
        return False

    def get_entry_by_id(self, id: str) -> Optional[Entry]:
        if (e := self.db.getByQuery({"id": id})): 
            return Entry.from_dict(e[0])

    def get_entry_by_exact_name(self, name: str) -> Optional[Entry]:
        if (e := self.db.getByQuery({'name': name})):
            if len(e) > 1:
                warnings.warn(f'Found {len(e)} entries for name {name}. Returning the first one.')
            return Entry.from_dict(e[0])

    def get_entries_by_name(self, name: str) -> List[Entry]:
        with self.db.lock:
            with open(self.db.filename, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            return list(map(Entry.from_dict, filter(lambda d: name in d['name'], db_data['data'])))

    def get_entries_by_name_regex(self, regex: str) -> List[Entry]:
        with self.db.lock:
            with open(self.db.filename, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            pattern = re.compile(regex)
            return list(map(Entry.from_dict, filter(lambda d: pattern.match(d['name']), db_data['data'])))

    def get_entries_between_dates(self, first: Union[datetime, int], second: Union[datetime, int]) -> List[Entry]:
        with self.db.lock:
            first, second = list(self.__convert_date_to_timestamp(first, second))
            with open(self.db.filename, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            return list(map(Entry.from_dict, filter(lambda d: first <= d['timestamp'] <= second, db_data['data'])))

    def get_entries_greater_than_date(self, date: Union[datetime, int]) -> List[Entry]:
        with self.db.lock:
            timestamp = next(self.__convert_date_to_timestamp(date))
            with open(self.db.filename, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            return list(map(Entry.from_dict, filter(lambda d: d['timestamp'] > timestamp, db_data['data'])))

    def get_entries_lower_than_date(self, date: Union[datetime, int]) -> List[Entry]:
        with self.db.lock:
            timestamp = next(self.__convert_date_to_timestamp(date))
            with open(self.db.filename, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            return list(map(Entry.from_dict, filter(lambda d: d['timestamp'] < timestamp, db_data['data'])))

    def __convert_date_to_timestamp(*dates: Iterable[Union[datetime, int]]) -> Generator[int, None, None]:
        for date in dates:
            if type(date) is not int:
                date = date.timestamp()
            yield date
