"""Functions and tools to deal with Houdini parameters."""

# Future
from __future__ import annotations

# Standard Library
import contextlib
import operator
import re
from typing import TYPE_CHECKING

# Houdini Core Tools
from houdini_core_tools import exceptions

# Houdini
import hou

if TYPE_CHECKING:
    from collections.abc import Callable

    StringTuple = tuple[str, ...]


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


def get_multiparm_containing_folders(
    name: str, parm_template_group: hou.ParmTemplateGroup
) -> tuple[hou.FolderParmTemplate, ...]:
    """Given a parameter template name, return a list of containing multiparms.

    If the name is contained in one or more multiparm folders, the returned templates
    will be ordered from innermost to outermost

    |_ outer
      |_ inner#
        |_ param#_#

    In a situation like above, querying for containing folders of param#_# would
    result in a tuple ordered as follows: (<hou.FolderParmTemplate inner#>,  <hou.FolderParmTemplate outer>)

    Args:
        name: The name of the parameter to get the containing names for.
        parm_template_group: A parameter template group for a nde.

    Returns:
        A tuple of containing multiparm templates, if any.
    """
    # A list of containing folders.
    containing_folders = []

    # Get the folder the parameter is in.
    containing_folder = parm_template_group.containingFolder(name)

    # Keep looking for containing folders until there are no.
    while True:
        # Add a containing multiparm folder to the list.
        if is_parm_template_multiparm_folder(containing_folder):
            containing_folders.append(containing_folder)

        # Try to find the parent containing folder.
        try:
            containing_folder = parm_template_group.containingFolder(containing_folder)

        # Not inside a folder so bail out.
        except hou.OperationFailed:
            break

    return tuple(containing_folders)


def get_multiparm_container_offsets(name: str, parm_template_group: hou.ParmTemplateGroup) -> tuple[int, ...]:
    """Given a parameter template name, return a list of containing multiparm folder offsets.

    If the name is contained in one or more multiparm folders, the returned offsets
    will be ordered outermost to innermost

    |_ outer (starting offset 0)
      |_ inner# (starting offset 1)
        |_ param#_#

    In a situation like above, querying for containing offsets of param#_# would
    result in a tuple ordered as follows: (0, 1)

    Args:
        name: The name of the parameter to get the containing offsets for.
        parm_template_group: A parameter template group for a nde.

    Returns:
        A tuple of containing multiparm offsets, if any.
    """
    # A list of contain folders.
    containing_folders = get_multiparm_containing_folders(name, parm_template_group)

    # The containing folder list is ordered by folder closest to the base parameter.
    # We want to process that list in reverse so the first offset item will be for the
    # outermost parameter and match the ordered provided by the user.
    return tuple(get_multiparm_start_offset(folder) for folder in reversed(containing_folders))


def get_multiparm_start_offset(parm_template: hou.ParmTemplate) -> int:
    """Get the start offset of items in the multiparm.

    Args:
        parm_template: A multiparm folder parm template

    Returns:
        The start offset of the multiparm.

    Raises:
        ParameterTemplateIsNotAMultiparmError: If the template is not a multiparm.
    """
    if not is_parm_template_multiparm_folder(parm_template):
        raise exceptions.ParameterTemplateIsNotAMultiparmError

    return int(parm_template.tags().get("multistartoffset", 1))


def is_parm_template_multiparm_folder(parm_template: hou.ParmTemplate) -> bool:
    """Returns True if the parm template represents a multiparm folder type.

    Args:
        parm_template: The parameter template to check.

    Returns:
        Whether the template represents a multiparm folder.
    """
    if not isinstance(parm_template, hou.FolderParmTemplate):
        return False

    return parm_template.folderType() in {
        hou.folderType.MultiparmBlock,
        hou.folderType.ScrollingMultiparmBlock,
        hou.folderType.TabbedMultiparmBlock,
    }


def is_parm_tuple_vector(parm_tuple: hou.ParmTuple) -> bool:
    """Check if the tuple is a vector parameter.

    Args:
        parm_tuple: The parm tuple to check.

    Returns:
        Whether the parameter tuple is a vector.
    """
    parm_template = parm_tuple.parmTemplate()

    return parm_template.namingScheme() == hou.parmNamingScheme.XYZW


def eval_parm_tuple_as_vector(
    parm_tuple: hou.ParmTuple,
) -> hou.Vector2 | hou.Vector3 | hou.Vector4:
    """Return the parameter value as a hou.Vector of the appropriate size.

    Args:
        parm_tuple: The parm tuple to eval.

    Returns:
        The evaluated parameter as a hou.Vector*

    Raises:
        ParmTupleTypeError: If the parm tuple is not a vector type (XYZW).
    """
    if not is_parm_tuple_vector(parm_tuple):
        raise exceptions.ParmTupleTypeError(parm_tuple, "vector")

    value = parm_tuple.eval()
    size = len(value)

    if size == 2:  # noqa: PLR2004
        return hou.Vector2(value)

    if size == 3:  # noqa: PLR2004
        return hou.Vector3(value)

    return hou.Vector4(value)


def is_parm_tuple_color(parm_tuple: hou.ParmTuple) -> bool:
    """Check if the parameter is a color parameter.

    Args:
        parm_tuple: The parm tuple to check.

    Returns:
        Whether the parameter tuple is a color.
    """
    parm_template = parm_tuple.parmTemplate()

    return parm_template.look() == hou.parmLook.ColorSquare


def eval_parm_tuple_as_color(parm_tuple: hou.ParmTuple) -> hou.Color:
    """Evaluate a color parameter and return a hou.Color object.

    Args:
        parm_tuple: The parm tuple to eval.

    Returns:
        The evaluated parameter as a hou.Vector*

    Raises:
        ParmTupleTypeError: If the parm tuple is not a color.
    """
    if not is_parm_tuple_color(parm_tuple):
        raise exceptions.ParmTupleTypeError(parm_tuple, "color chooser")

    return hou.Color(parm_tuple.eval())


def eval_parm_as_strip(parm: hou.Parm) -> tuple[bool, ...]:
    """Evaluate the parameter as a Button/Icon Strip.

    Returns a tuple of True/False values indicated which buttons
    are pressed.

    Args:
        parm: The parm to eval.

    Returns:
        True/False values for the strip.

    Raises:
        ParameterNotAButtonStripError: If the parameter is not a button strip.
    """
    parm_template = parm.parmTemplate()

    if not isinstance(parm_template, hou.MenuParmTemplate) or not parm_template.isButtonStrip():
        raise exceptions.ParameterNotAButtonStripError(parm)

    # Get the value.  This might be the selected index, or a bit mask if we
    # can select more than one.
    value = parm.eval()

    # Initialize a list of False values for each item on the strip.
    num_items = len(parm_template.menuItems())
    values = [False] * num_items

    # If our menu type is a Toggle that means we can select more than one
    # item at the same time so our value is really a bit mask.
    if parm_template.menuType() == hou.menuType.StringToggle:
        # Check which items are selected.
        for i in range(num_items):
            mask = 1 << i

            if value & mask:
                values[i] = True

    # Value is just the selected index so set that one to True.
    else:
        values[value] = True

    return tuple(values)


def eval_parm_strip_as_string(parm: hou.Parm) -> StringTuple:
    """Evaluate the parameter as a Button Strip as strings.

    Returns a tuple of the string tokens which are enabled.

    Args:
        parm: The parm to eval.

    Returns:
        String token values.
    """
    strip_results = eval_parm_as_strip(parm)

    menu_items = parm.parmTemplate().menuItems()

    enabled_values = []

    for i, value in enumerate(strip_results):
        if value:
            enabled_values.append(menu_items[i])

    return tuple(str(val) for val in enabled_values)


def is_parm_multiparm(parm: hou.Parm | hou.ParmTuple) -> bool:
    """Check if this parameter is a multiparm.

    Args:
        parm: The parm or tuple to check for being a multiparm.

    Returns:
        Whether the parameter is a multiparm.
    """
    # Get the parameter template for the parm/tuple.
    parm_template = parm.parmTemplate()

    return is_parm_template_multiparm_folder(parm_template)
