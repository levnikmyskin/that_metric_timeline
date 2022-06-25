from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, NewType, List, Dict, Optional
from abc import ABC
from tmt.info import __version__
import typing
import json



Timestamp = NewType('Timestamp', int)

@dataclass
class BaseJsonDataclass(ABC):
    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        init_dict = {}
        for key, val in typing.get_type_hints(cls).items():
            field = cls.__solve_type(val, key, d)
            init_dict[key] = field
        return cls(**init_dict)

    @classmethod
    def from_json(cls, s: str):
        return cls.from_dict(json.loads(s))

    @staticmethod
    def __solve_type(t, key, d):
        args = typing.get_args(t)
        if len(args) == 0:
            if t is Timestamp:
                return d.get(key)
            elif issubclass(t, BaseJsonDataclass):
                return BaseJsonDataclass.init_subclass(t, key, d)
            else:
                return d.get(key)
        if BaseJsonDataclass.__is_optional_type(args):
            if d.get(key):
                return BaseJsonDataclass.__solve_type(args[0], key, d)
            return None

        container = typing.get_origin(t)
        if len(args) == 1:  # in our case, this is a list
            arg = args[0]
            arg_args = typing.get_args(arg)

            if len(arg_args) == 0:
                return container(arg.from_dict(e) if hasattr(arg, 'from_dict') else arg(e) for e in d.get(key))
            else:
                return container(BaseJsonDataclass.__solve_type(arg, 'l', {'l': e}) for e in d.get(key))
        else:
            raise ValueError('There might be a Tuple or some kind of container which is not a list somewhere in the models. This is not supported yet')

    @staticmethod
    def init_subclass(subcls, key: str, kvs: Dict):
        if key in kvs:
            return subcls.from_dict(kvs[key])
        return None

    @staticmethod
    def __is_optional_type(args):
        return len(args) > 1 and typing.get_origin(args[1]) is None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Result(BaseJsonDataclass):
    entry_id: str
    name: str
    path: str


@dataclass
class Metric(BaseJsonDataclass):
    entry_id: str
    name: str
    value: float


@dataclass
class Entry(BaseJsonDataclass):
    id: str
    name: str
    args: str
    date_created: Timestamp
    local_results_path: str
    local_snapshot_path: str = ""
    date_saved: Optional[Timestamp]  = None
    metrics: List[Metric] = field(default_factory=list)
    other_runs: List[Entry] = field(default_factory=list)
    results: List[Result] = field(default_factory=list)
    version: str = __version__