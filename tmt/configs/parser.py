from __future__ import annotations
import os
import json
from tmt.history.snapshot import SnapshotManager
from tmt.storage.schema import BaseJsonDataclass
from dataclasses import dataclass

CONFIG_PATH = '.tmt/config.json'

@dataclass
class Configs(BaseJsonDataclass):
    """
    This dataclass holds the `tmt` configuration options. Users should not mind about this class, since this is 
    used internally by other `tmt` functions such as :py:func:`tmt.decorators.recorder.recorder` or :py:class:`tmt.utils.manager.TmtManager`. When instantiated with :py:func:`tmt.configs.parser.Configs.from_default_path_or_default_config()`, it will look
    for a json configuration file in the default path `.tmt/config.json`.
    If none is found, it will create `tmt` default configuration. See :doc:`Configuration <configuration>`.
    """
    tmt_dir: str
    snapshot_source: str
    snapshot_target: str
    last_snapshot_link: str
    gitignore_path: str
    json_db_path: str 
    results_path: str 

    @classmethod 
    def from_dict(cls, d):
        config = super().from_dict(d)
        config.snapshot_target = os.path.join(config.tmt_dir, config.snapshot_target)
        config.last_snapshot_link = os.path.join(config.tmt_dir, config.last_snapshot_link)
        config.json_db_path = os.path.join(config.tmt_dir, config.json_db_path)
        config.results_path = os.path.join(config.tmt_dir, config.results_path)
        return config

    @staticmethod
    def from_config(path: str = CONFIG_PATH) -> Configs:
        with open(path, 'r') as f:
            return Configs.from_dict(json.load(f))

    @staticmethod
    def from_default_path_or_default_config() -> Configs:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return Configs.from_dict(json.load(f))
        return Configs.default_config()

    @staticmethod
    def default_config() -> Configs:
        return Configs(
            tmt_dir='.tmt',
            snapshot_source=os.getcwd(),
            snapshot_target='.tmt/snapshots',
            last_snapshot_link='.tmt/snapshots/last',
            gitignore_path=os.path.join(os.getcwd(), '.gitignore'),
            json_db_path=".tmt/tmt_db.json",
            results_path=".tmt/results"
        )

    def init_snapshot_manager(self, id: str):
        return SnapshotManager(
            id=id,
            tmt_dir=self.tmt_dir,
            snapshot_source=self.snapshot_source,
            snapshot_target=self.snapshot_target,
            last_snapshot_link=self.last_snapshot_link,
            ignore_path=self.gitignore_path
        )
