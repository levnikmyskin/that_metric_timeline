from tmt.history.context import context_manager
from typing import Any


def save(obj: Any, name: str, allow_exist=False, extension='.pkl') -> str:
    context = context_manager.get()
    if context is None:
        raise ValueError("`save` function was called before initializing the context. Did you use a tmt decorator/class?")
    return context.save(obj, name, allow_exist, extension)