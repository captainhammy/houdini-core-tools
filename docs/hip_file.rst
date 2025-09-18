.. currentmodule:: houdini_core_tools.hip_file

==============
Hip File Tools
==============

The :mod:`~houdini_core_tools.hip_file` module provides tools related to dealing with a Houdini scene/session.

check_unsaved_changes
---------------------

:func:`check_unsaved_changes` is a function decorator that can be used to wrap a function where you want to ensure
the current hip file is saved before execution. This is useful as an automated pre-check for operations that require
the hip to be saved, such as submitting to a render farm.

.. code-block:: python

    @check_unsaved_changes()
    def submit():
        """Submit to the farm."""
        print("Submitted!")

When the wrapped function is called and there are no unsaved changes, the function will execute as expected:

.. code-block:: python

    >>> submit()
    Submitted!

However, if there are unsaved changes, it will raise an exception:

.. code-block:: python

    >>> submit()
    Traceback (most recent call last):
      File "<console>", line 1, in <module>
      File "python/houdini_core_tools/hip_file.py", line 99, in wrapper
      raise hou.OperationFailed("Hip file has unsaved changes")  # noqa: TRY003
      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    hou.OperationFailed: The attempted operation failed.
    Hip file has unsaved changes

The decorator accepts a ``prompt`` parameter and when ``True``, will prompt the user on whether to save and continue, or
abort.

.. image:: images/prompt_unsaved_changes.png

.. code-block:: python

    >>> submit()
    Traceback (most recent call last):
      File "<console>", line 1, in <module>
      File "python/houdini_core_tools/hip_file.py", line 95, in wrapper
        raise hou.OperationFailed("Hip file save declined")  # noqa: TRY003
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    hou.OperationFailed: The attempted operation failed.
    Hip file save declined


The prompt execution is wrapped in UI available check so if the code is being executed non-graphically it will be skipped
and the check will fail.

get_hip_save_time_from_file
---------------------------

The :func:`get_hip_save_time_from_file` function will parse the start of the hip file to try and determine
when it was last saved by using the value of $_HIP_SAVETIME.

The result is returned as a :class:`datetime.datetime` object.

.. code-block:: python

    >>> get_hip_save_time_from_file("/path/to/a/file.hip")
    datetime.datetime(2025, 2, 5, 5, 33, 57)


get_hip_save_version_from_file
------------------------------

The :func:`get_hip_save_version_from_file` function will parse the start of the hip file to try and determine
the version of Houdini last used to save the hip file by using the value of $_HIP_SAVEVERSION.

The result is returned as a tuple of integers, similar to :func:`hou.applicationVersion`.

.. code-block:: python

    >>> get_hip_save_version_from_file("/path/to/a/file.hip")
    (20, 5, 493)

hip_save_time
-------------

The :func:`hip_save_time` function will try and determine when the current hip file was last saved.

The result is returned as a :class:`datetime.datetime` object if the file exists, otherwise :const:`None`.

.. code-block:: python

    >>> hip_save_time()
    datetime.datetime(2025, 2, 5, 5, 33, 57)


hip_save_version
----------------

The :func:`hip_save_version` function will try and determine the version of Houdini last used to save the current
hip file.

The result is returned as a tuple of integers, similar to :func:`hou.applicationVersion`, if the file exists, otherwise
:const:`None`.

.. code-block:: python

    >>> hip_save_version()
    (20, 5, 493)



hip_version
-----------

The :func:`hip_version` function can be used to quickly grab the major version
from a hip file name.  It does this by simply looking for a ``v##`` string in the name and grabbing the number. In
the event multiples are contained, the last one is used. Any version number is ``%02d`` padded.

.. code-block::

    untitled.hip -> None
    hipname_v00.hip -> "00"
    hipname_v01.hip -> "01"
    hipname.v01.hip -> "01"
    hipname_v00003.hip -> "03"
    hipname_v02.03.hip -> "02"
    hipname_v05_alternate_v01.hip -> "01"
    hipname_v3021.hip -> "3021"

save_copy
---------

Unless you're super familiar with the intricacies of Houdini files it's not readily apparent how you would go about
saving off a copy of your current session while not saving over the currently open file.  It's not complex, but
:func:`save_copy` will handle the small bit of work to do it.

.. code-block:: python

    >>> hou.hipFile.path()
    '/var/tmp/test.hip'
    >>> hou.hipFile.hasUnsavedChanges()
    True
    >>> save_copy("/var/tmp/copy_of_test.hip")
    >>> hou.hipFile.hasUnsavedChanges()
    True

As previously mentioned, the current state of the session is saved to the new path and the original file remains
unchanged with the changes since last change remaining unsaved.

set_frame_range
---------------

The :func:`set_frame_range` function is a convenience function which handles updating
Houdini's frame and playback ranges to the supplied values.  If the current frame is outside of the new range it will
be set to the first frame.

.. code-block:: python

    >>> hou.playbar.frameRange()
    <hou.Vector2 [1, 240]>
    >>> hou.playbar.playbackRange()
    <hou.Vector2 [1, 240]>
    >>> hou.frame()
    1.0
    >>>
    >>> set_frame_range(1001, 1010)
    >>>
    >>> hou.playbar.frameRange()
    <hou.Vector2 [1001, 1010]>
    >>> hou.playbar.playbackRange()
    <hou.Vector2 [1001, 1010]>
    >>> hou.frame()
    1001.0

