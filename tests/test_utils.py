import os

from tests import BaseTest
from tmt import tmt_recorder, tmt_save
from tmt.utils.manager import TmtManager
import numpy as np

from tmt.history.context import context_manager
from tmt.storage.json_db import DbManager

returned_metrics = {'f1': 0.87, 'acc': 0.45, 'loss': 1e-4}


def custom_save(obj, path):
    np.save(path, obj)


def custom_save_path(obj, _):
    path = 'tests/custom_save.npy'
    np.save('tests/custom_save.npy', obj)
    return path


@tmt_recorder('test_exp_custom_save', config_path='tests/test_config.json')
def decorated_fn(_):
    # do something
    tmt_save(returned_metrics, name='test_metrics', extension='.npy', custom_save=custom_save)
    return returned_metrics


@tmt_recorder('test_exp_custom_save_path', config_path='tests/test_config.json')
def decorated_fn_path(_):
    # do something
    arr = np.array([0])
    tmt_save(arr, name='test_metrics', extension='.npy', custom_save=custom_save_path)
    return returned_metrics


class TestUtils(BaseTest):

    def tearDown(self):
        super().tearDown()
        os.remove('tests/custom_save.npy')

    def test_custom_save(self):
        _ = decorated_fn(None)
        entry = context_manager.get().entry
        db_man = DbManager(context_manager.get().config.json_db_path)
        db_entry = db_man.get_entry_by_id(entry.id)
        self.assertEqual(len(db_entry.results), 1)
        self.assertEqual(db_entry.results[0].path[-4:], '.npy')
        np.load(db_entry.results[0].path, allow_pickle=True)
        _ = decorated_fn_path(None)
        entry = context_manager.get().entry
        db_man = DbManager(context_manager.get().config.json_db_path)
        db_entry = db_man.get_entry_by_id(entry.id)
        self.assertEqual(len(db_entry.results), 1)
        self.assertEqual(db_entry.results[0].path, 'tests/custom_save.npy')
        self.assertEqual(np.load(db_entry.results[0].path), np.array([0]))

        manager = TmtManager(config='tests/test_config.json')
        manager.set_entry_by_name("test_exp_custom_save_path")
        gen = manager.load_results()
        self.assertWarns(UserWarning, next, gen)
