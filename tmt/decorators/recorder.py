from typing import Callable, Dict, Optional
from tmt.history.context import ContextManager, context_manager
from tmt.storage.json_db import DbManager
from tmt.storage.schema import Metric
from datetime import datetime


def recorder(name: str, config_path: Optional[str] = None, save_on_exception=False):
    """One of the main `tmt` functions. This is a decorator which can be used to keep track of 
    experiments, saving metrics, results and taking a snapshot of the code at this moment in time

    :param name: name used to save this experiment in the database
    :type name: str
    :param config_path: if you want to use a custom configuration file, specify the path. Defaults to None
    :type config_path: Optional[str], optional
    :param save_on_exception: save everything (snapshot, metrics etc.) even if an exception happens. Defaults to False
    :type save_on_exception: bool, optional
    """
    def inner(func: Callable[..., Optional[Dict[str, float]]]):
        def wrapper(*args, **kwargs) -> Optional[Dict[str, float]]:
            cm = ContextManager(name, config_path)
            context_manager.set(cm)
            db_manager = DbManager(cm.config.json_db_path)
            try:
                metrics = func(*args, **kwargs)
                if metrics:
                    for k, v in metrics.items():
                        cm.entry.metrics.append(Metric(cm.entry.id, k, v))
                cm.snap_manager.make_snapshot()
                cm.entry.date_saved = int(datetime.now().timestamp())
                db_manager.add_new_entries([cm.entry])
                return metrics
            except Exception as e:
                if not save_on_exception:
                    raise e
                cm.snap_manager.make_snapshot()
                cm.entry.date_saved = int(datetime.now().timestamp())
                db_manager.add_new_entries([cm.entry])
            
        return wrapper
    return inner
