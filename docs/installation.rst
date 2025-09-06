============
Installation
============

------
Source
------

In order to install this tool you'll first need to get a copy of the files from `Github <https://github.com/captainhammy/houdini-core-tools>`_. You
can either clone the repository or download and extract an official release.

-----------------
Adding to Houdini
-----------------

``houdini-core-tools`` supports being loaded into Houdini in multiple ways:

    - `Rez packages <https://rez.readthedocs.io/en/stable/>`_
    - `Houdini Packages <https://www.sidefx.com/docs/houdini/ref/plugins.html>`_
    - Standard path based setup

^^^^^^^^^^^^
Rez Package
^^^^^^^^^^^^

This package supports Rez packaging via a ``package.py`` file in the root directory.

^^^^^^^^^^^^^^^
Houdini Package
^^^^^^^^^^^^^^^

This tool comes with a ``houdini_core_tools.json`` file which can be used to tell Houdini how to load
the package. Add the containing directory to ``$HOUDINI_PACKAGE_DIR`` or one of the other methods defined
`here <https://www.sidefx.com/docs/houdini/ref/plugins.html#using_packages>`_

^^^^^^^^^^^^^^^^
Path Based Setup
^^^^^^^^^^^^^^^^

In order to manually setup the tooling you'll need to do the following:

    - Add the ``src/houdini`` path to ``$HOUDINI_PATH``
    - Add the ``src/python`` path to ``$PYTHONPATH``

------------
Requirements
------------

Package requirements are listed in ``requirements.txt``, as well as defined in the Rez ``package.py``. Please ensure
they are installed prior to launching Houdini.
