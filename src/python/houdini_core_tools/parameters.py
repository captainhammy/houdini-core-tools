"""Functions and tools to deal with Houdini parameters."""

# Future
from __future__ import annotations

# Standard Library
import contextlib
import operator
import re
from typing import Callable

# Houdini
import hou

# Non-Public Functions


def _find_parameters_with_value(target_value: str, check_func: Callable) -> tuple[hou.Parm, ...]:
    """Find parameters which contain the target value.

    Args:
        target_value: The string value to search for.
        check_func: A function to use for testing value matching.

    Returns:
        A tuple of parameters which contain the value.
    """
    # Use 'opfind' hscript command to find all the nodes which have parameters
    # containing our value.
    paths = hou.hscript(f"opfind '{target_value}'")[0].split()

    parms_with_value = []

    for path in paths:
        node = hou.node(path)

        for parm in node.parms():
            value = None

            # Check string parameters via unexpandedString()
            try:
                value = parm.unexpandedString()

            # Fails on non-string parameters.
            except hou.OperationFailed:
                # In that case, check for any expressions.
                with contextlib.suppress(hou.OperationFailed):
                    value = parm.expression()

            # If we got a value and the checking function detects a match then
            # we'll return that parameter
            if value and check_func(value, target_value):
                parms_with_value.append(parm)

    return tuple(parms_with_value)


# Functions


def find_matching_parent_parm(parm: hou.Parm, *, stop_at_locked_hda: bool = True) -> hou.Parm | None:
    """Look for a parameter of the same name on any parent node.

    Args:
        parm: The reference parameter whose name to search for.
        stop_at_locked_hda: Whether to stop if a parent is a locked HDA.

    Returns:
        The matching parent parameter, if any.
    """
    node = parm.node()

    parent = node.parent()

    parm_name = parm.name()

    while parent is not None:
        parent_parm = parent.parm(parm_name)

        if parent_parm is not None:
            return parent_parm

        if parent.isLockedHDA() and stop_at_locked_hda:
            return None

        parent = parent.parent()

    return None


def find_parameters_using_variable(variable: str) -> tuple[hou.Parm, ...]:
    """Find parameters which contain a variable.

    This only works for string parameters

    The variable name can be supplied with or without a $.

    Variable usage that includes {} to help with disambiguation will also be automatically found.

    This will match only the exact usage.  For example, if you
    search for $HIP the result would not include any parameters
    using $HIPNAME or $HIPFILE.

    Args:
        variable: The variable name to search for.

    Returns:
        A tuple of parameters which contain the variable.
    """
    search_variable = variable.replace("{", "").replace("}", "")

    # If the variable doesn't start with $ we need to add it.
    if not variable.startswith("$"):
        search_variable = "$" + search_variable

    disambiguated_variable = f"${{{search_variable[1:]}}}"

    def _checker(value, target_variable):  # type: ignore
        # We need to escape the $ since it's a special regex character.
        var = "\\" + target_variable

        # Regex to match the variable string but ensuring that it matches exactly.
        # For example of you are looking for $HIP you want to ensure you don't also
        # match $HIPNAME or $HIPFILE
        return bool(re.search(f"(?=.*{var}(?![a-zA-Z]))", value))

    results: list[hou.Parm] = []

    for variable_to_test in (search_variable, disambiguated_variable):
        results.extend(_find_parameters_with_value(variable_to_test, _checker))

    return tuple(results)


def find_parameters_with_value(target_value: str) -> tuple[hou.Parm, ...]:
    """Find parameters which contain the target value.

    This only works for string parameters.

    Args:
        target_value: The value to search for.

    Returns:
        A tuple of parameters which contain the value.
    """
    return _find_parameters_with_value(target_value, operator.contains)
