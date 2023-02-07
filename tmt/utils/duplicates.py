import enum
from dataclasses import dataclass


class DuplicatePolicy(enum.Enum):
    """
    Enum class used to be used with :py:class:`tmt.utils.duplicates.DuplicateStrategy`.
    Possible choices are:

    #. NO_ALLOW: do not allow duplicate names (i.e., throws :py:exc:`tmt.exceptions.DuplicatedNameError`);
    #. AS_SUB_ENTRY: allow duplicate names, insert this new one as a "sub-entry" of the pre-existing one;
    #. AS_NEW_ENTRY: allow duplicate names, create a completely new entry with the same name of the previous one
       (entries are still identified by a unique UUID).

    Having an entry as a "sub-entry" of another one means that it will be saved in the `entry.others` field.
    The sub-entry won't be directly searchable. Using a sub-entry is especially useful when running a task
    (e.g. experiment)
    which is somehow connected to that entry and still part of that previous task.

    .. note::
        When :py:meth:`tmt.utils.manager.TmtManager.load_results` is called on an entry with a sub-entry, results
        for the sub-entry will be returned as well.

    .. note::
        Specifying an entry as a sub-entry will still take a snapshot of the current code etc. Nothing changes in how
        the entry is saved and processed, except for what stated before.

    .. warning::
        If you specify :py:attr:`tmt.utils.duplicates.DuplicateStrategy.AS_SUB_ENTRY` and there are multiple entries
        with the same name already available, `tmt` cannot tell which one you would like to use. You can specify a
        `parent_id` when creating :py:class:`tmt.utils.duplicates.DuplicateStrategy`. Otherwise, the last created entry
        will be used.
    """
    DONT_ALLOW = enum.auto()
    AS_SUB_ENTRY = enum.auto()
    AS_NEW_ENTRY = enum.auto()


@dataclass
class DuplicateStrategy:
    """
    Data class used with :py:class:`tmt.decorators.recorder` to decide how to handle duplicates.
    `parent_id` is used when :py:class:`tmt.utils.duplicates.DuplicatePolicy.AS_SUB_ENTRY` is specified and more than one
    entry is found for a given name. In this case, if you don't specify a valid `parent_id`, a warning will be raised
    and the last created entry (with the given name) will be used as the parent.
    """
    policy: DuplicatePolicy = DuplicatePolicy.DONT_ALLOW
    parent_id: str = ""
