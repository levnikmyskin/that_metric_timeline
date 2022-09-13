from tmt.history.snapshot import *
import unittest


class TestHistory(unittest.TestCase):
    def setUp(self):
        self.snap = SnapshotManager('test_id', 'tests', 'tests/snapshot_test', 'tests/fake_project', 'tests/snapshot_test/last', 'tests/.gitignore')
        self.new_folder = os.path.join(self.snap.snapshot_source, 'new_folder')

    def tearDown(self):
        if os.path.exists(self.snap.snapshot_target):
            shutil.rmtree(self.snap.snapshot_target)
        if os.path.exists(self.snap.last_snapshot_link):
            os.remove(self.snap.last_snapshot_link)
        if os.path.exists(self.new_folder):
            shutil.rmtree(self.new_folder)

    def test_make_first_snapshot(self):
        self.assertFalse(os.path.exists(self.snap.last_snapshot_link))
        self.snap.make_snapshot()
        self.__assert_no_diff()
        self.assertTrue(os.path.islink(self.snap.last_snapshot_link))
        self.assertEqual(os.readlink(self.snap.last_snapshot_link), self.snap.snapshot_dest)

    def test_make_snapshot_with_diff(self):
        if not os.path.exists(self.snap.last_snapshot_link):
            self.test_make_first_snapshot()
        diff_file = os.path.join(self.snap.snapshot_source, '__init__.py')
        with open(diff_file, 'a') as f:
            f.write('\nprint("test")')
        init = self.snap.__dict__
        init['id'] = 'test_id_1'
        del init['snapshot_dest']
        self.snap.make_snapshot()
        self.__assert_no_diff()
        self.assertTrue(os.readlink(self.snap.last_snapshot_link), self.snap.snapshot_dest)
        for root, _, files in os.walk(self.snap.snapshot_dest):
            for f in files:
                if f in self.snap.gitignored_files:
                    continue
                if os.path.join(root, f) == os.path.join(self.snap.snapshot_dest, '__init__.py'):
                    continue
                self.assertTrue(os.stat(os.path.join(root, f)).st_nlink > 1)
        with open(diff_file, 'w') as f:
            f.write('')

    def test_make_snapshot_with_new_folder(self):
        if not os.path.exists(self.snap.last_snapshot_link):
            self.test_make_first_snapshot()
        os.mkdir(self.new_folder)
        with open(os.path.join(self.new_folder, 'test.py'), 'w') as f:
            f.write('print("")')
        init = self.snap.__dict__
        init['id'] = 'test_id_1'
        del init['snapshot_dest']
        self.snap.make_snapshot()
        self.__assert_no_diff()

    def test_make_first_snapshot_without_ignore(self):
        self.snap.ignore_path = None
        self.test_make_first_snapshot()
        self.tearDown()
        self.snap.ignore_path = ''
        self.test_make_first_snapshot()
    
    def test_make_snapshot_with_diff_without_ignore(self):
        self.snap.ignore_path = None
        self.test_make_snapshot_with_diff()
        self.tearDown()
        self.setUp()
        self.snap.ignore_path = ''
        self.test_make_snapshot_with_diff()

    def __assert_no_diff(self):
        cmp = dircmp(self.snap.snapshot_source, self.snap.snapshot_dest)
        self.assertEqual(list(self.snap.get_diff_files(cmp, self.snap.snapshot_source)), [])
        return cmp
