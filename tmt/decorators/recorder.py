from typing import Callable, Dict, Optional
from tmt.history.context import ContextManager, context_manager
from tmt.storage.json_db import DbManager
from tmt.storage.schema import Metric
from datetime import datetime

from tmt.utils.duplicates import DuplicateStrategy


def recorder(name: str, config_path: Optional[str] = None, save_on_exception=False, description="", duplicate_strategy=DuplicateStrategy()):
    """
    One of the main ``tmt`` functions. This is a decorator which can be used to keep track of 
    experiments, saving metrics, results and taking a snapshot of the code at this moment in time.

    .. note::
        For simplicity, ``tmt`` exposes this function from its root, with the ``tmt_recorder`` name. This is the 
        recommended way of importing this function, i.e. ``from tmt import tmt_recorder``.

    **Usage**:

    .. code-block:: python

        from tmt import tmt_recorder 

        @tmt_recorder(name="some_experiment")
        def train_and_predict(x_tr, y_tr, x_te, y_te):
            lr = LogisticRegression()
            lr.fit(x_tr, y_tr)
            preds = lr.predict(x_te)
            return {'f1': f1_score(y_te, preds), 'accuracy': accuracy_score(y_te, preds)} 

    :param name: name used to save this experiment in the database.
    :type name: str
    :param config_path: if you want to use a custom configuration file, specify the path. Defaults to None.
        See :doc:`configuration` and :py:class:`tmt.configs.parser.Configs`
    :type config_path: Optional[str], optional
    :param save_on_exception: save everything (snapshot, metrics etc.) even if an exception happens. Defaults to False.
    :type save_on_exception: bool, optional
    :param description: experiment description. Can be as long as you wish.
    :type description: str, optional
    :param duplicate_strategy: strategy to use when `name` already exists in the database. By default, set to
        :py:attr:`tmt.utils.duplicates.DuplicateStrategy.DONT_ALLOW`.
    :type duplicate_strategy: DuplicateStrategy, optional
    :raises tmt.exceptions.DuplicatedNameError: if `name` already exists in the database,
        and :py:class:`tmt.utils.duplicates.DuplicateStrategy` is `DONT_ALLOW`.
    """
    def inner(func: Callable[..., Optional[Dict[str, float]]]):
        def wrapper(*args, **kwargs) -> Optional[Dict[str, float]]:
            cm = ContextManager(name, config_path, duplicate_strategy=duplicate_strategy, description=description)
            context_manager.set(cm)
            db_manager = DbManager(cm.config.json_db_path)
            try:
                metrics = func(*args, **kwargs)
                if metrics:
                    for k, v in metrics.items():
                        cm.entry.metrics.append(Metric(cm.entry.id, k, v))
                cm.snap_manager.make_snapshot()
                cm.entry.date_saved = int(datetime.now().timestamp())
                db_manager.add_or_update_entry(cm.root_entry)
                return metrics
            except Exception as e:
                if not save_on_exception:
                    raise e
                cm.snap_manager.make_snapshot()
                cm.entry.date_saved = int(datetime.now().timestamp())
                db_manager.add_or_update_entry(cm.root_entry)

        return wrapper
    return inner
