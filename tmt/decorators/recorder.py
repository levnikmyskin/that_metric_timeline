from typing import Callable, Dict, Optional
from tmt.history.context import ContextManager, context_manager
from tmt.storage.json_db import DbManager
from tmt.storage.schema import Metric
from datetime import datetime


def recorder(name: str, config_path: Optional[str] = None, save_on_exception=False):
    def inner(func: Callable[..., Dict[str, float]]):
        def wrapper(*args, **kwargs):
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
                cm.entry.date_saved = int(datetime.now().timestamp())
                db_manager.add_new_entries([cm.entry])
            
        return wrapper
    return inner
