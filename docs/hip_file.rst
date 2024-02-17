.. currentmodule:: houdini_core_tools.hip_file

==============
Hip File Tools
==============

The :mod:`~houdini_core_tools.hip_file` module provides tools related to dealing with a Houdini scene/session.

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

