from tmt.storage.json_db import DbManager
from tmt.storage.schema import Entry, Metric
from tmt.configs.parser import Configs
from typing import Optional, Generator, Any, Tuple, List
from tmt.exceptions import EntryNotFound
import pickle


class TmtManager:
    """
    This is a rather minimalistic helper class which you can use to load experiments, load pickled results, see metrics and so on.
    The recommended way of looking for an experiment is using `tmt` terminal user interface (see :ref:`TMT TUI <tmttui>`).
    Once you have a unique id or name, you can use one of the setter methods to set the :py:class:`tmt.storage.schema.Entry` (i.e., an experiment) to be 
    used with this instance. If you want low-level access to the json database (read-only operations), you can access the `db` member.

    **Usage**:

    .. code-block:: python

        from tmt import TmtManager

        # Let's say we know there is an experiment with id "example"


        # An Entry is a row in the database, i.e. an experiment that was tracked.
        manager = TmtManager()
        manager.set_entry_by_id('example') 

        # load the results and unpickle them
        for name, path in manager.results_paths():
            with open(path, 'rb') as f:
                # do stuff with your results. If it's a pickle it's 
                # more convenient to use the code block below this one
                res = pickle.load(f)

        # load the unpickled results
        for name, res in manager.load_results():
            # do something with your results.
            # if res is a numpy array...
            print(res.mean())


        for name, val in manager.get_metrics():
            print(f"{name}: {val}")

        # If you need to do other stuff, like searching for 
        # experiments between two datetimes and so on
        # you can access the `db` member like
        manager.db.get_entries_greater_than_date(date_or_timestamp)

    :param entry: this is an entry in the json database, i.e. a previously tracked and saved experiments.
    :type entry: Optional[Entry]
    :param config: this can be a path to a custom configuration json file. See :doc:`Configuration <configuration>`.
    :type config: Optional[str]
    """

    def __init__(self, entry: Optional[Entry] = None, config: Optional[str] = None):
        if config is None:
            self.config = Configs.from_default_path_or_default_config()
        else:
            self.config = Configs.from_config(config)
        self.db = DbManager(self.config.json_db_path, read_only=True)
        self.entry = entry

    def set_entry_by_name(self, name: str) -> Entry:
        if (e := self.db.get_entry_by_exact_name(name)):
            self.entry = e
            return self.entry
        raise EntryNotFound(f'No entry (experiment) found for name {name}')

    def set_entry_by_id(self, id: str) -> Entry:
        if (e := self.db.get_entry_by_id(id)):
            self.entry = e
            return self.entry
        raise EntryNotFound(f'No entry (experiment) found for id {id}')

    def entry_not_none(func):
        def inner(*args, **kwargs):
            assert args[0].entry is not None, "This instance has not an `Entry` associated with it. Use one of the several `set_` methods"
            return func(*args, **kwargs)
        return inner
    
    @entry_not_none
    def load_results(self) -> Generator[Tuple[str, Any], None, None]:
        """
        Creates a generator which yields a tuple with the name of the results (see :py:func:`tmt.history.utils.save`)
        and the unpickled object. See also :py:func:`tmt.utils.manager.TmtManager.results_paths` if you just want the paths.

        :yield: A tuple with (name, object) of each result stored with this experiment.
        :rtype: Generator[Tuple[str, Any], None, None]
        """
        for result in self.entry.results:
            with open(result.path, 'rb') as f:
                yield result.name, pickle.load(f)

    @entry_not_none
    def results_paths(self) -> Generator[Tuple[str, str], None, None]:
        """
        Creates a generator which yields a tuple with the name of the results (see :py:func:`tmt.history.utils.save`)
        and its path on disk. See also :py:func:`tmt.utils.manager.TmtManager.load_results` if you want unpickled objects.

        :yield: A tuple with (name, path) of each result stored with this experiment.
        :rtype: Generator[Tuple[str, str], None, None]
        """
        for result in self.entry.results:
            yield result.name, result.path

    @entry_not_none
    def get_metrics(self) -> List[Metric]:
        return self.entry.metrics

    @entry_not_none
    def code_snapshot_path(self) -> str:
        """
        Returns the path to the code snapshot backup saved with this experiment.

        :return: path to the snapshot saved with this experiment.
        :rtype: str
        """
        return self.entry.local_snapshot_path
