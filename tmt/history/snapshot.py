from filecmp import dircmp
from dataclasses import dataclass
from functools import cached_property
from typing import Set, Optional
import itertools
import pathspec
import os
import shutil


@dataclass
class SnapshotManager:
    id: str
    tmt_dir: str
    snapshot_target: str
    snapshot_source: str
    last_snapshot_link: str
    ignore_path: Optional[str] = None

    @cached_property
    def gitignored_files(self) -> Set[str]: 
        ignore_tmt = {self.tmt_dir}
        if not self.ignore_path or not os.path.exists(self.ignore_path):
            return ignore_tmt
        with open(self.ignore_path, 'r') as f:
            spec = pathspec.PathSpec.from_lines('gitwildmatch', f)
        ignore_tmt.update(spec.match_tree(self.snapshot_source))
        return ignore_tmt
    
    @cached_property
    def snapshot_dest(self) -> str:
        return os.path.join(os.path.abspath(self.snapshot_target), self.id)

    def make_snapshot(self):
        if not os.path.exists(self.last_snapshot_link):
            self.copy_files()
            return
        last_snapshot_path = os.readlink(self.last_snapshot_link)
        cmp = dircmp(self.snapshot_source, last_snapshot_path)
        os.makedirs(self.snapshot_dest, exist_ok=True)
        for push_file in itertools.chain(self.get_diff_files(cmp, ''), self.get_new_files(cmp, '')):
            os.makedirs(os.path.join(self.snapshot_dest, os.path.dirname(push_file)), exist_ok=True)
            if os.path.isfile(os.path.join(self.snapshot_source, push_file)):
                shutil.copy(os.path.join(self.snapshot_source, push_file), os.path.join(self.snapshot_dest, push_file))
        for eq_file in self.get_equal_files(cmp, ''):
            os.makedirs(os.path.join(self.snapshot_dest, os.path.dirname(eq_file)), exist_ok=True)
            if os.path.isfile(os.path.join(self.snapshot_source, eq_file)):
                os.link(os.path.join(last_snapshot_path, eq_file), os.path.join(self.snapshot_dest, eq_file))
        self.create_symlink()

    def copy_files(self):
        shutil.copytree(self.snapshot_source, self.snapshot_dest, ignore=shutil.ignore_patterns(*self.gitignored_files))
        self.create_symlink()

    def create_symlink(self):
        if os.path.exists(self.last_snapshot_link):
            os.remove(self.last_snapshot_link)
        os.symlink(self.snapshot_dest, self.last_snapshot_link)

    @staticmethod
    def get_diff_files(cmp: dircmp, directory: str):
        for n in cmp.diff_files:
            yield os.path.join(directory, n)
        for d, sub_cmp in cmp.subdirs.items():
            yield from SnapshotManager.get_diff_files(sub_cmp, os.path.join(directory, d))

    @staticmethod
    def get_new_files(cmp: dircmp, directory: str):
        for n in cmp.left_only:
            yield os.path.join(directory, n)
        for d, sub_cmp in cmp.subdirs.items():
            yield from SnapshotManager.get_new_files(sub_cmp, os.path.join(directory, d))

    @staticmethod
    def get_removed_files(cmp: dircmp, directory: str):
        for n in cmp.right_only:
            yield os.path.join(directory, n)
        for d, sub_cmp in cmp.subdirs.items():
            yield from SnapshotManager.get_removed_files(sub_cmp, os.path.join(directory, d))

    @staticmethod
    def get_equal_files(cmp: dircmp, directory: str):
        for n in cmp.same_files:
            yield os.path.join(directory, n)
        for d, sub_cmp in cmp.subdirs.items():
            yield from SnapshotManager.get_equal_files(sub_cmp, os.path.join(directory, d))