tmt.utils package
=================

Submodules
----------

tmt.utils.manager module
------------------------

.. automodule:: tmt.utils.manager
   :show-inheritance:
   :noindex:

.. autoclass:: TmtManager
   :members:
   :show-inheritance:

   .. method:: load_results
      
      Creates a generator which yields a tuple with the name of the results (see :py:func:`tmt.history.utils.save`)
      and the unpickled object. See also :py:func:`tmt.utils.manager.TmtManager.results_paths` if you just want the paths.

      :yield: A tuple with (name, object) of each result stored with this experiment.
      :rtype: Generator[Tuple[str, Any], None, None]

   .. method:: results_paths

      Creates a generator which yields a tuple with the name of the results (see :py:func:`tmt.history.utils.save`)
      and its path on disk. See also :py:func:`tmt.utils.manager.TmtManager.load_results` if you want unpickled objects.

      :yield: A tuple with (name, path) of each result stored with this experiment.
      :rtype: Generator[Tuple[str, str], None, None]

   .. method:: code_snapshot_path

      Returns the path to the code snapshot backup saved with this experiment.

      :return: path to the snapshot saved with this experiment.
      :rtype: str

Module contents
---------------

.. automodule:: tmt.utils
   :members:
   :undoc-members:
   :show-inheritance:
