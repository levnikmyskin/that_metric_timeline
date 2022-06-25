import unittest
import os
from tmt.storage.schema import *
from tmt.storage.json_db import DbManager
from datetime import datetime
from tmt.configs.parser import Configs


@dataclass
class T1(BaseJsonDataclass):
    a: int
    b: typing.List[int]
    c: typing.Optional[typing.List[str]]
    d: typing.Optional[str]
    e: typing.List[typing.List[int]]


@dataclass
class T2(BaseJsonDataclass):
    t1: T1
    t2: typing.Optional[T1]


class TestSchema(unittest.TestCase):

    def setUp(self):
        self.conf = Configs.from_config('tests/test_config.json')

    def tearDown(self):
        if os.path.exists(self.conf.json_db_path + '.lock'):
            os.remove(self.conf.json_db_path + '.lock')
        if os.path.exists(self.conf.json_db_path):
            os.remove(self.conf.json_db_path) 

    def test_from_dict(self):
        d = {'a': 3, 'b': [1,2,3], 'c': ['x', 'y', 'z'], 'd': 'd', 'e': [[1,2], [3,4]]}
        d2 = {'a': 3, 'b': [1,2,3], 'c': None, 'd': None, 'e': [[1,2], [3,4]]}
        d3 = {'t1': d, 't2': d2}
        d4 = {'t1': d, 't2': None}
        t1 = T1.from_dict(d)
        for k, v in d.items():
            self.assertEqual(getattr(t1, k), v)
        t2 = T1.from_dict(d2)
        for k, v in d2.items():
            self.assertEqual(getattr(t2, k), v)

        t3 = T2.from_dict(d3)
        self.assertTrue(isinstance(t3.t1, T1))
        self.assertTrue(isinstance(t3.t2, T1))

        t4 = T2.from_dict(d4)
        self.assertTrue(isinstance(t4.t1, T1))
        self.assertIsNone(t4.t2)

    def test_from_json(self):
        import copy
        d = {'id': 0, 'name': 'test', 'date_created': int(datetime.now().timestamp()), 'local_results_path': '', 'metrics': [
            {'name': 'm', 'value': 0.0}, {'name': 'm1', 'value': 0.0}
        ], 'other_runs': [], 'results': []}
        Entry.from_json(json.dumps(d))
        d['other_runs'] = [copy.deepcopy(d)]
        Entry.from_json(json.dumps(d))

    def test_delete_entry(self):
        db = DbManager(self.conf.json_db_path)
        entry = Entry('test', 'test', '', 0, '', '')
        db.add_new_entries([entry])
        self.assertTrue(db.delete_entry(entry))
