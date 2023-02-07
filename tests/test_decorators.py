import warnings
from tmt import tmt_recorder
from tmt.storage.json_db import DbManager
from tmt.history.context import context_manager, ContextManager, Configs
from tmt.history.utils import save
from tmt.exceptions import DuplicatedNameError
from tmt.utils.duplicates import *
from tests import BaseTest
import os
import pickle


returned_metrics = {'f1': 0.87, 'acc': 0.45, 'loss': 1e-4}


@tmt_recorder('test_exp', config_path='tests/test_config.json')
def decorated_fn(_):
    # do something
    save(returned_metrics, name='test_metrics')
    return returned_metrics


class TestDecorators(BaseTest):

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
        self.assertRaises(DuplicatedNameError, ContextManager, 'test_exp', 'tests/test_config.json')

    def test_duplicates(self):
        def test_fn(_):
            save(returned_metrics, name='test_metrics')
            return returned_metrics

        db_man = DbManager(self.conf.json_db_path)
        db_man.delete_all()
        fn = tmt_recorder('test_exp', config_path='tests/test_config.json')(test_fn)
        _ = fn(None)
        self.assertRaises(DuplicatedNameError, fn, None)
        fn = tmt_recorder('test_exp', config_path='tests/test_config.json', duplicate_strategy=DuplicateStrategy(DuplicatePolicy.AS_NEW_ENTRY))(test_fn)
        self.assertEqual(returned_metrics, fn(None))
        parent_id = context_manager.get().entry.id
        entries = db_man.get_entries_by_name("test_exp")
        self.assertEqual(len(entries), 2)
        for e in entries:
            self.assertEqual(len(e.other_runs), 0)

        # test sub entries
        fn = tmt_recorder('test_exp', config_path='tests/test_config.json', duplicate_strategy=DuplicateStrategy(DuplicatePolicy.AS_SUB_ENTRY))(test_fn)
        self.assertEqual(returned_metrics, fn(None))
        self.assertWarns(UserWarning, fn, None)
        fn = tmt_recorder('test_exp', config_path='tests/test_config.json', duplicate_strategy=DuplicateStrategy(DuplicatePolicy.AS_SUB_ENTRY, parent_id))(test_fn)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            self.assertEqual(returned_metrics, fn(None))
            self.assertEqual(0, len(w))
        entries = db_man.get_entries_by_name("test_exp")
        self.assertEqual(len(entries), 2)
        for e in entries:
            if e.id == parent_id:
                self.assertTrue(1 <= len(e.other_runs) <= 3)

    def test_description(self):
        def test_fn(_):
            return returned_metrics
        db_man = DbManager(self.conf.json_db_path)
        db_man.delete_all()
        desc = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore 
        magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo 
        consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        """
        fn = tmt_recorder('test_exp', config_path='tests/test_config.json', description=desc)(test_fn)
        _ = fn(None)
        entry = context_manager.get().entry
        db_man = DbManager(context_manager.get().config.json_db_path)
        db_entry = db_man.get_entry_by_id(entry.id)
        self.assertEqual(db_entry.description, desc)

