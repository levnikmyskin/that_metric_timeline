from tmt import tmt_recorder
from tmt.storage.json_db import DbManager
from tmt.history.context import context_manager, ContextManager, Configs
from tmt.history.utils import save
from tmt.exceptions import DuplicatedNameError
import unittest
import os
import shutil
import pickle


returned_metrics = {'f1': 0.87, 'acc': 0.45, 'loss': 1e-4}


@tmt_recorder('test_exp', config_path='tests/test_config.json')
def decorated_fn(_):
    # do something
    save(returned_metrics, name='test_metrics')
    return returned_metrics


class TestDecorators(unittest.TestCase):
    def setUp(self) -> None:
        self.conf = Configs.from_config('tests/test_config.json')

    def tearDown(self) -> None:
        if os.path.exists(self.conf.json_db_path + '.lock'):
            os.remove(self.conf.json_db_path + '.lock')
        os.remove(self.conf.json_db_path)

        if os.path.exists(context_manager.get().snap_manager.snapshot_target):
            shutil.rmtree(context_manager.get().snap_manager.snapshot_target)
        if os.path.exists(context_manager.get().snap_manager.last_snapshot_link):
            os.remove(context_manager.get().snap_manager.last_snapshot_link)
        shutil.rmtree(self.conf.results_path)

    def test_recorder(self):
        metrics = decorated_fn(None)
        self.assertEqual(metrics, returned_metrics)
        self.assertIsInstance(context_manager.get(), ContextManager)
        entry = context_manager.get().entry
        db_man = DbManager(context_manager.get().config.json_db_path)
        db_entry = db_man.get_entry_by_id(entry.id)
        self.assertEqual(entry.to_dict(), db_entry.to_dict())
        self.assertTrue(os.path.exists(context_manager.get().snap_manager.snapshot_dest))
        self.assertTrue(os.path.exists(context_manager.get().get_save_path()))
        self.assertTrue(len(entry.metrics) > 0)

        # test results saving 
        self.assertTrue(os.path.exists(context_manager.get().get_save_path_with_name(name='test_metrics') + '.pkl'))
        with open(context_manager.get().get_save_path_with_name(name='test_metrics') + '.pkl', 'rb') as f:
            self.assertEqual(pickle.load(f), returned_metrics)
        self.assertTrue(len(entry.results) > 0)
        self.assertRaises(DuplicatedNameError, ContextManager, 'test_exp', 'tests/test_config.json', allow_duplicate_names=False)
