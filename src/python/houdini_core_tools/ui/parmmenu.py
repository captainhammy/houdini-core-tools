"""This module contains functions supporting custom PARMmenu.xml entries."""

# Future
from __future__ import annotations

# Houdini
import hou

# Non-Public Functions


def _check_valid_to_convert(parm: hou.Parm, reference_indicator: str) -> bool:
    """Check if a parameter is valid to convert the reference of.

    A parameter is valid if it is a node reference string parameter with a raw
    value that starts with the reference indicator.

    Args:
        parm: There parameter to check.
        reference_indicator: The target indicator to check against.

    Returns:
        Whether the parm can be converted.
    """
    parm_template = parm.parmTemplate()

    # Check if the parameter is a string parameter and if so, a node reference.
    if (
        isinstance(parm_template, hou.StringParmTemplate)
        and parm_template.stringType() == hou.stringParmType.NodeReference
    ):
        # Need to test values to decide whether to show up or not.
        path = parm.eval()

        # Ignore empty strings.
        if not path:
            return False

        # Ignore paths which already seem to be the desired indicator.
        if not path.startswith(reference_indicator):
            return False

        # Can't convert parameters with keyframes/expressions.
        if parm.keyframes():
            return False

        # If the path is the same as the raw path then we can say that we
        # can show the menu item.  If the path is not the same as the
        # unexpanded we won't say yes because it would be some sort of
        # expression which we don't want to mess with.
        if path == parm.unexpandedString() and parm.evalAsNode() is not None:
            return True

    return False


def _valid_to_convert_to_absolute_reference(parm: hou.Parm) -> bool:
    """Check if a parameter is valid to convert to an absolute reference.

    A parameter is valid if it is a node reference string parameter with a raw
    value appears to be a relative path and points to a valid node.

    Args:
        parm: There parameter to check.

    Returns:
        Whether the parm can be converted.
    """
    return _check_valid_to_convert(parm, "..")


def _valid_to_convert_to_relative_reference(parm: hou.Parm) -> bool:
    """Check if a parameter is valid to convert to a relative reference.

    A parameter is valid if it is a node reference string parameter with a raw
    value appears to be an absolute path and points to a valid node.

    Args:
        parm: There parameter to check.

    Returns:
        Whether the parm can be converted.
    """
    return _check_valid_to_convert(parm, "/")


# Functions


def convert_absolute_to_relative_path(scriptargs: dict) -> None:
    """Convert any absolute node paths to relative paths.

    Args:
        scriptargs: kwargs dict from PARMmenu entry.
    """
    parms = scriptargs["parms"]

    for parm in parms:
        if _valid_to_convert_to_relative_reference(parm):
            target_node = parm.evalAsNode()

            parm.set(parm.node().relativePathTo(target_node))


def convert_absolute_to_relative_path_context(scriptargs: dict) -> bool:
    """Context script for converting any absolute node paths to relative paths.

    The menu entry will be shown if there are node reference string parameters
    whose values are absolute paths.

    Args:
        scriptargs: kwargs dict from PARMmenu entry.

    Returns:
        Whether to show the menu entry.
    """
    parms = scriptargs["parms"]

    return any(_valid_to_convert_to_relative_reference(parm) for parm in parms)


def convert_relative_to_absolute_path(scriptargs: dict) -> None:
    """Convert any absolute node paths to absolute paths.

    Args:
        scriptargs: kwargs dict from PARMmenu entry.
    """
    parms = scriptargs["parms"]

    for parm in parms:
        if _valid_to_convert_to_absolute_reference(parm):
            target_node = parm.evalAsNode()

            parm.set(target_node.path())


def convert_relative_to_absolute_path_context(scriptargs: dict) -> bool:
    """Context script for converting any relative node paths to absolute paths.

    The menu entry will be shown if there are node reference string parameters
    whose values are relative paths.

    Args:
        scriptargs: kwargs dict from PARMmenu entry.

    Returns:
        Whether to show the menu entry.
    """
    parms = scriptargs["parms"]

    return any(_valid_to_convert_to_absolute_reference(parm) for parm in parms)
