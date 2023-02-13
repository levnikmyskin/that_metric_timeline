Snapshots
*********

How does ``tmt`` save snapshots?
==============================

Every time you track an experiment with ``tmt_recorder`` (:py:func:`tmt.decorators.recorder.recorder`), a code snapshot backup will be saved (by default in ``.tmt/snapshots``). This means that: 

 - the first time you use the library in your project, a simple copy of your project is made (by default, this is the current working directory (*cwd*) from which you launch the experiment); 
 - subsequent backups will only copy new and different files, while hard-linking all other files. This limits the space taken on your disk; 
 - by default, the library will look for a ``.gitignore`` file in your *cwd* and ignore (i.e., not copy) all files listed in there (the `PathSpec <https://python-path-specification.readthedocs.io/en/latest/readme.html>`_ library is used for gitignore parsing);
 - a symlink pointing to the last snapshot taken is created (and updated everytime) in ``.tmt/snapshots/last``.  

You can change the default paths by using a :doc:`configuration` file.

How do I use these snapshots?
=============================

With ``tmt`` snapshots you can take a look at the state of your code when you tracked the experiment. This should make it easier to 
reproduce your experiments (and also to find out how the hell you got that 0.9 F1 that you can't seem to achieve anymore anyhow).

You can use ``tmt`` terminal user interface, ``tmt_tui`` (see :ref:`tmttui`), to search for an experiment and retrieve the code 
snapshot path on your sistem. Unfortunately, at the moment there is no quick way to switch between one experiment' snapshot to the other's, but it will probably come in a future release.

On the other hand, these snapshots are indeed only saved on your local machine. Your data remain yours and there is no cloud or 
account involved.
