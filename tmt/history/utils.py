from tmt.history.context import context_manager
from typing import Any


def save(obj: Any, name: str, allow_exist=False, extension='.pkl') -> str:
    """
    This function can be used to save any `pickable <https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled>`_. object you may want to save when running your experiments.
    It must be called by a function decorated with :py:func:`tmt.decorators.recorder.recorder` (or within code called from that function).

    .. note::
        For simplicity, `tmt` exposes this function from its root with the `tmt_save` name. You can import it with `from tmt import 
        tmt_save`

    What this function does is not too far from simply doing:

    .. code-block:: python

        with open(library_path + name, 'wb') as f:
            pickle.dump(obj, f)
    
    Using this function however, we make sure that `tmt` knows where all of your pickled objects are so that you can 
    later easily retrieve them.

    **Usage**:

    .. code-block:: python

        from tmt import tmt_recorder, tmt_save

        @tmt_recorder(name="some_experiment_with_data")
        def train_and_predict(...):
            ...
            preds = lr.predict(x_te)
            tmt_save(preds, name='lr_predictions')
            return {'f1': f1_score(y_te, preds), 'accuracy': accuracy_score(y_te, preds)}

    :param obj: the object you want to save, must be pickable.
    :type obj: Any
    :param name: the object will be saved with this name. Use a name that will help you recognize this object in the future.
    :type name: str
    :param allow_exist: if True, allows this object to be saved even if the name already exists. Defaults to False.
    :type allow_exist: bool, optional
    :param extension: the extension to save the file with, defaults to '.pkl'.
    :type extension: str, optional
    :raises ValueError: this is raised if the function is illegaly called outside a function decorated with :py:func:`tmt.decorators.recorder.recorder`
    :raises tmt.exceptions.DuplicatedNameError: if `name` already exists and `allow_exist` is False, this exception will be raised.
    :return: the path where the object was saved. `tmt` will take care of storing it, so you can ignore this return value.
    :rtype: str
    """
    context = context_manager.get()
    if context is None:
        raise ValueError("`save` function was called before initializing the context. Did you use a tmt decorator/class?")
    return context.save(obj, name, allow_exist, extension)