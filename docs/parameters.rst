.. currentmodule:: houdini_core_tools.parameters

===============
Parameter Tools
===============

The :mod:`~houdini_core_tools.parameters` module provides tools for finding parameters.

find_matching_parent_parm
-------------------------

The :func:`find_matching_parent_parm` function offers the ability to search for a parameter on a parent node
with the same name.  This can be useful for things like ROP nodes where you might want to evaluate a parent
node script parameter if it exists.

The ``stop_at_locked_hda`` parameter is used to decide what will happen in the event that a parent node is a locked
HDA and whether to continue on up.  This check occurs **after** the first occurrence of the parent check so that if
the parameter's node's parent is actually a locked HDA it will still be checked as normal and any locked behavior will
occur after the initial check.

find_parameters_using_variable
------------------------------

The :func:`find_parameters_using_variable` function will search a hip session and report any parameters which are using
a particular environment variable.

**This only works for string parameters**

Including **$** in the variable name is optional.  The function will also search for any possible disambiguated usage (eg.
$HIP or ${HIP})

The following calls would all result in the same results:

.. code-block:: python

    >>> find_parameters_using_variable("HIP")
    (<hou.Parm rendergallerysource in /stage>, <hou.Parm taskgraphfile in /tasks/topnet1>, <hou.Parm checkpointfile in
    /tasks/topnet1>, <hou.Parm pdg_workingdir in /tasks/topnet1/localscheduler>)
    >>> find_parameters_using_variable("$HIP")
    # same as above
    >>> find_parameters_using_variable("${HIP}")
    # same as above

find_parameters_with_value
--------------------------

The :func:`find_parameters_with_value` function will search a hip session and report any parameters whose non-evaluated
value contains the exact ``target_value``.

**This only works for string parameters**

.. code-block:: python

    >>> houdini_core_tools.parameters.find_parameters_with_value("localscheduler")
    (<hou.Parm topscheduler in /tasks/topnet1>,)
    >>> houdini_core_tools.parameters.find_parameters_with_value("localschedule")
    # This returns nothing as the string must be an exact and full match.
    ()

