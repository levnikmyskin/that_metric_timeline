import unittest
import os
import shutil
from tmt import Configs
from tmt.history.context import context_manager


class BaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.conf = Configs.from_config('tests/test_config.json')

    def tearDown(self) -> None:
        if os.path.exists(self.conf.json_db_path + '.lock'):
            os.remove(self.conf.json_db_path + '.lock')
        if os.path.exists(self.conf.json_db_path):
            os.remove(self.conf.json_db_path)

        if context_manager.get() is None:
            return
        if os.path.exists(context_manager.get().snap_manager.snapshot_target):
            shutil.rmtree(context_manager.get().snap_manager.snapshot_target)
        if os.path.exists(context_manager.get().snap_manager.last_snapshot_link):
            os.remove(context_manager.get().snap_manager.last_snapshot_link)
        shutil.rmtree(self.conf.results_path)
