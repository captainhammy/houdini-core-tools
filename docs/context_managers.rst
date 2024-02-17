.. currentmodule:: houdini_core_tools.context_managers

================
Context Managers
================

The :mod:`~houdini_core_tools.context_managers` module provides a number of useful Python context managers which can be
used to manage the state of Houdini when doing various actions.

emit_varchange
--------------

If you update the value of a Houdini related variable in a session, it will not automatically cause any nodes which
reference it to become dirty and need to recook.  To force any variable changes to dirty their consuming nodes it is
necessary to use the `varchange <https://www.sidefx.com/docs/houdini/commands/varchange.html>`_ hscript command.

The :func:`emit_varchange` context manager allows you to perform any variable updates
within the scope of the manager and have a **varchange** signal emitted upon exit.


.. code-block:: python

    >>> with emit_varchange():
    ...    hou.hscript("set FOO=456")

Multiple calls can be nested and the varchange will be emitted when the outermost manager exists.

The varchange signal will still be emitted in the event an exception occurs.


temporarily_unlock_parameters
-----------------------------

It is very common in pipelines to set a bunch of parameters with specific values/data and then lock them. Often times
these parameters will eventually need to be updated and it can be tedious to manage all the unlocking and locking of
the parameters.  The :func:`temporarily_unlock_parameters` context manager
allows you to more easily handle this.

By passing a single :class:`hou.Parm`, :class:`hou.ParmTuple`, or an iterable of :class:`hou.Parm`,
the unlocking and subsequent locking of those items are automatically handled for you.

.. code-block:: python

    >>> box_scale_parm = hou.parm("/obj/geo/box1/scale")
    >>> print(box_scale_parm.eval())
    1.0
    >>> box_scale_parm.lock(True)
    >>> with temporarily_unlock_parameters(box_scale_parm):
    ...    box_scale_parm.set(3)
    ...
    >>> print(box_scale_parm.eval())
    3.0

In the event the parameter cannot have its lock status changed, a :class:`hou.PermissionError` will be raised and indicate
which parameter failed. This commonly occurs if the parameter is inside a locked digital asset, or not included in a take.

All parameters will have their lock state restored in the event of an exception.

.. code-block:: python

    >>> with temporarily_unlock_parameters(box_scale_parm):
    ...     box_scale_parm.set(3)
    ...
    Traceback (most recent call last):

    ...

    hou.PermissionError: Error setting lock status for /obj/geo/box1/scale

restore_current_selection
-------------------------

Various operations in Houdini may change the current selection. As this is not always desirable, the
:func:`restore_current_selection` context manager will ensure the currently
selected nodes are still selected after the fact.

.. code-block:: python

    >>> with restore_current_selection():
    ...     # Perform actions that could change the selection.
    ...

The selection will be restored in the event of an exception.


set_temporary_update_mode
-------------------------

Various operations in Houdini may result in Houdini attempting to start cooking. When these operations are part of a series
of events (such as building a network, adjusting parameters, etc) this is not always desirable. The
:func:`set_temporary_update_mode` context manager can be used to temporarily set
the UI update mode to a desired value and restore it after the block is complete.

.. code-block:: python

    >>> with set_temporary_update_mode(hou.updateMode.Manual):
    ...     # Perform actions while in manual mode.
    ...

The update mode will be restored in the event an exception occurs.
