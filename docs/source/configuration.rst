Configuration
*************

``tmt`` can be used as-is and does not require any configuration file. By default, everything the library needs or save is stored in 
a ``.tmt`` hidden directory, in the current working directory(*cwd*). If your *cwd* changes often for different experiments, or if you want to specify which folder is backed up and more, you may want to create and specify a custom configuration file.  
  
To do so, create a ``config.json`` file: if you're fine with using the ``cwd/.tmt`` directory, place this file in ``cwd/.tmt/config.json``. This way, you won't have to specify the path to this configuration file to library related functions.  
The configuration file has the following structure:

.. code-block:: c 

    {
        // tmt_dir specifies the path where code snapshots and 
        // results will be saved. You may use an absolute 
        // path as well
        "tmt_dir": ".example",

        // this is the folder we will take a snapshot of 
        // for every experiment  
        "snapshot_source": ".", 

        // snapshot_target is where code snapshots will be 
        // saved. It will be joined with tmt_dir. So in this 
        // case the target will be .examples/snapshot_example
        "snapshot_target": "snapshot_example",

        // this path will be a symlink to the last snapshot
        // taken. Same rules as for snapshot_target apply
        "last_snapshot_link": "snapshot_example/last",

        // this might actually be any file with a .gitignore 
        // syntax. These files will be ignored and not backupped
        "gitignore_path": "path/to/.gitignore",

        // the two paths below are for the db and the results
        // directory, respectively. Same rules apply as for 
        // snapshot_target, so path will be .example/tmt_db.json
        "json_db_path": "tmt_db.json",
        "results_path": "results"
    }

.. warning::

    The example above has C-like comments ``//``. These were used for better readability but they're not valid JSON comments.
    Don't use them in your real configuration file.

As mentioned, if you save this file in ``.tmt/config.json``, no other action is necessary and ``tmt`` will pick it up and use it for its configuration.  
If instead you save it somewhere else, say ``/config/path/config.json``, you will have to specify this path in the code. When recording experiments:

.. code-block:: python
    :emphasize-lines: 1

    @tmt_recorder('custom_config', config_path='/config/path/config.json')
    def with_custom_config():
        x, y = make_classification()
        lr = LogisticRegression()
        lr.fit(x, y)
        preds = lr.predict(x)
        return {'f1': f1_score(y, preds), 'accuracy': accuracy_score(y, preds)}

And when managing experiments:

.. code-block:: python

    manager = TmtManager(config='/config/path/config.json')
    # do your stuff