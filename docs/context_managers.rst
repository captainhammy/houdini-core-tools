.. currentmodule:: houdini_core_tools.context_managers

================
Context Managers
================

The :mod:`~houdini_core_tools.context_managers` module provides a number of useful Python context managers which can be
used to manage the state of Houdini when doing various actions.


context_container
-----------------

One thing Houdini doesn't immediately provide you with is a convenient way to getting a parent node for an arbitrary
node type you might wish to create. This is where the :func:`context_container` comes in. This context manager takes
a :class:`hou.NodeTypeCategory` and returns an appropriate node which can be used to create a node of that type.

The node that is returned may be an existing manager type node (e.g. ``/obj`` for Object nodes), or a newly created node (a
Geometry Object to create a SOP node under.)

For categories which need to create a new node, the ``destroy`` parameter (which defaults to ``True``) will cause the
node to be deleted after the context manager scope ends. This is particularly helpful for testing of nodes where you
want to create a node, run tests against it, then have it removed to no longer pollute a session.  Setting
``destroy=False`` will prevent it from being removed automatically.

If an unknown category value is passed, a :exc:`~houdini_core_tools.exceptions.UnsupportedCategoryError` will be raised.

Mappings
********
Node type category names are mapped either directly (to existing nodes) or indirectly (to node types which will be created).

Direct Mappings
^^^^^^^^^^^^^^^

The following node type categories have direct mappings to existing nodes which will be returned:

+---------+--------+
| Context | Node   |
+=========+========+
| Driver  | /out   |
+---------+--------+
| Lop     | /stage |
+---------+--------+
| Object  | /obj   |
+---------+--------+
| Shop    | /shop  |
+---------+--------+
| Vop     | /mat   |
+---------+--------+


New Container Mappings
^^^^^^^^^^^^^^^^^^^^^^

The following node type categories will generate a node of the parent type which will be returned:

+---------+---------------+
| Context | Parent Type   |
+=========+===============+
| Cop     | CopNet/copnet |
+---------+---------------+
| Cop2    | CopNet/img    |
+---------+---------------+
| Dop     | Object/dopnet |
+---------+---------------+
| Sop     | Object/geo    |
+---------+---------------+
| Top     | Object/topnet |
+---------+---------------+

.. code-block:: python

    # In this example, we want to create a Box SOP and that the container type that is
    # created is a Geometry Object. As we have left the `destroy` parameter at its default
    # value, after the context manager has gone out of scope we can see that the box was
    # destroyed and raises the expected exception trying to access it.
    >>> with context_container(hou.sopNodeTypeCategory()) as container:
    ...     assert container.type() == hou.nodeType("Object/geo")
    ...     box = container.createNode("box")
    >>> box.path()
    Traceback (most recent call last):
      File "<console>", line 1, in <module>
      File "/opt/hfs20.5/houdini/python3.11libs/hou.py", line 14085, in path
        return _hou.NetworkMovableItem_path(self)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    hou.ObjectWasDeleted: Attempt to access an object that no longer exists in Houdini

    # In this example, we set destroy=False to ensure the node will not be removed.
    >>> with context_container(hou.sopNodeTypeCategory(), destroy=False) as container:
    ...     box = container.createNode("box")
    >>> box.path()
    '/obj/geo1/box1'


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

set_current_node
----------------

The :func:`set_current_node` context manager will set the current working node (:func:`hou.pwd()`) to the supplied node
for the duration, then restore it afterwards.

.. code-block:: python

    >>> hou.pwd()
    <hou.OpNode at />
    >>> with set_current_node(hou.node("/obj")):
    ...     hou.pwd()
    ...
    <hou.OpNode at /obj>
    >>> hou.pwd()
    <hou.OpNode at />


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
