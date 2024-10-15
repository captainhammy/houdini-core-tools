"""Functions and tools to deal with Houdini parameters."""

# Future
from __future__ import annotations

# Standard Library
import contextlib
import itertools
import operator
import re
from typing import TYPE_CHECKING

# Houdini Core Tools
from houdini_core_tools import exceptions

# Houdini
import hou

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


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


def _get_names_in_folder(parent_template: hou.FolderParmTemplate) -> tuple[str, ...]:
    """Get a list of template names inside a template folder.

    This should only really ever be called originally with a multiparm template.

    Args:
        parent_template: The parm template to get items for.

    Returns:
        A list of template names inside the template.
    """
    names: list[str] = []

    for parm_template in parent_template.parmTemplates():
        if isinstance(parm_template, hou.FolderParmTemplate):
            # If the template is a folder (but not a multiparm folder) then we
            # need to get the parms inside it as well since they are technically siblings.
            if not is_parm_template_multiparm_folder(parm_template):
                names.extend(_get_names_in_folder(parm_template))

            else:
                names.append(parm_template.name())

        else:
            names.append(parm_template.name())

    return tuple(str(name) for name in names)


def _validate_multiparm_resolve_values(name: str, indices: Sequence[int]) -> None:
    """Validate a multiparm token string and the indices to be resolved.

    This function will raise a ValueError if there are not enough indices
    supplied for the number of tokens.

    Args:
        name: The parameter name to validate.
        indices: The indices to format into the token string.

    Raises:
        NotEnoughMultiParmIndicesError: When not enough indices are supplied.
    """
    # Get the number of multiparm tokens in the name.
    token_count = name.count("#")

    # Ensure that there are enough indices for the name.  Houdini can handle too many
    # indices but if there are not enough it won't like that and return an unexpected value.
    if token_count > len(indices):
        raise exceptions.NotEnoughMultiParmIndicesError(name, token_count, len(indices))


# Functions


def eval_multiparm_instance(
    node: hou.OpNode,
    name: str,
    indices: list[int] | tuple[int] | int,
    *,
    raw_indices: bool = False,
) -> tuple | float | str | hou.Ramp:
    """Evaluate a multiparm parameter by indices.

    The name should include the # value(s) which will be replaced by the indices.

    The index should be the multiparm index, not including any start offset.

    You cannot try to evaluate a single component of a tuple parameter, evaluate
    the entire tuple instead and get which values you need.

    # Float
    >>> eval_multiparm_instance(node, "float#", 1)
    0.53
    # Float 3
    >>> eval_multiparm_instance(node, "vec#", 1)
    (0.53, 1.0, 2.5)

    Args:
        node: The node to evaluate the parameter on.
        name: The base parameter name.
        indices: The multiparm indices.
        raw_indices: Whether the indices are 'raw' and should not try and take the folder offset into account.

    Returns:
        The evaluated parameter value.

    Raises:
        MissingMultiParmTokenError: If the parameter name does not contain at least one '#'.
        NoMatchingParameterTemplate: If the parameter name does not exist.
        InvalidMultiParmIndicesError: If the multiparm indices are not valid.
    """
    if "#" not in name:
        raise exceptions.MissingMultiParmTokenError(name)

    ptg = node.parmTemplateGroup()

    parm_template = ptg.find(name)

    if parm_template is None:
        raise exceptions.NoMatchingParameterTemplate(name, node)

    # Handle directly passing a single index.
    if not isinstance(indices, (list, tuple)):
        indices = [indices]

    if not raw_indices:
        offsets = get_multiparm_container_offsets(name, ptg)

        # Adjust any supplied offsets with the multiparm offset.
        indices = [idx + offset for idx, offset in zip(indices, offsets)]

    # Validate that enough indices were passed.
    _validate_multiparm_resolve_values(name, indices)

    # Resolve the name and indices to get the parameter name.
    full_name = resolve_multiparm_tokens(name, indices)

    parm_tuple = node.parmTuple(full_name)

    if parm_tuple is None:
        raise exceptions.InvalidMultiParmIndicesError(full_name)

    values = parm_tuple.eval()

    # Return single value for non-tuple parms.
    if len(values) == 1:
        return values[0]

    return tuple(values)


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


def eval_parm_strip_as_string(parm: hou.Parm) -> tuple[str, ...]:
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


def get_multiparm_siblings(parm: hou.Parm | hou.ParmTuple) -> dict:
    """Get a tuple of any sibling parameters in the multiparm block.

    Args:
        parm: The parameter to get any siblings for.

    Returns:
        Any sibling parameters.

    Raises:
        ParameterIsNotAMultiParmInstanceError: If the parm is not a multiparm instance.
    """
    if not parm.isMultiParmInstance():
        raise exceptions.ParameterIsNotAMultiParmInstanceError(parm.name())

    if isinstance(parm, hou.Parm):
        parm = parm.tuple()

    # Get the template name for the parameter.
    template_name = get_multiparm_template_name(parm)

    node = parm.node()

    ptg = node.parmTemplateGroup()

    # Find the most immediate containing multiparm folder.
    containing_template = get_multiparm_containing_folders(template_name, ptg)[0]  # type: ignore

    # Get a list of template names in that folder.
    names = _get_names_in_folder(containing_template)

    # The instance indices of the parameter.
    # indices = get_multiparm_instance_indices(parm, instance_index=True)
    indices = parm.multiParmInstanceIndices()

    parms = {}

    for name in names:
        # Skip the parameter that was passed in.
        if name == template_name:
            continue

        # Resolve the tokens and get the parm tuple.
        parm_name = resolve_multiparm_tokens(name, indices)
        parm_tuple = node.parmTuple(parm_name)

        # If the parm tuple has a size of 1 then just get the parm.
        if len(parm_tuple) == 1:
            parm_tuple = parm_tuple[0]

        parms[name] = parm_tuple

    return parms


def get_multiparm_start_offset(parm_template: hou.ParmTemplate) -> int:
    """Get the start offset of items in the multiparm.

    Args:
        parm_template: A multiparm folder parm template

    Returns:
        The start offset of the multiparm.

    Raises:
        ParameterTemplateIsNotAMultiParmError: If the template is not a multiparm.
    """
    if not is_parm_template_multiparm_folder(parm_template):
        raise exceptions.ParameterTemplateIsNotAMultiParmError

    return int(parm_template.tags().get("multistartoffset", 1))


def get_multiparm_template_name(parm: hou.Parm | hou.ParmTuple) -> str | None:  # type: ignore  # noqa: RET503
    """Return a multiparm instance's parameter template name.

    Args:
        parm: The parm to get the multiparm instances values for.

    Returns:
        The parameter template name, or None
    """
    # Return None if the parameter isn't a multiparm instance.
    if not parm.isMultiParmInstance():
        return None

    if isinstance(parm, hou.Parm):
        parm = parm.tuple()

    parm_template = parm.parmTemplate()

    indices = parm.multiParmInstanceIndices()
    parent_muliparm = parm.parentMultiParm()

    parent_template = parent_muliparm.parmTemplate()

    for template in parent_template.parmTemplates():  # pragma: no branch
        resolved_name = resolve_multiparm_tokens(template.name(), indices)

        if resolved_name == parm_template.name():
            return template.name()


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


def is_parm_tuple_color(parm_tuple: hou.ParmTuple) -> bool:
    """Check if the parameter is a color parameter.

    Args:
        parm_tuple: The parm tuple to check.

    Returns:
        Whether the parameter tuple is a color.
    """
    parm_template = parm_tuple.parmTemplate()

    return parm_template.look() == hou.parmLook.ColorSquare


def is_parm_tuple_vector(parm_tuple: hou.ParmTuple) -> bool:
    """Check if the tuple is a vector parameter.

    Args:
        parm_tuple: The parm tuple to check.

    Returns:
        Whether the parameter tuple is a vector.
    """
    parm_template = parm_tuple.parmTemplate()

    return parm_template.namingScheme() == hou.parmNamingScheme.XYZW


def resolve_multiparm_tokens(name: str, indices: int | list[int] | tuple[int, ...]) -> str:
    """Resolve a multiparm token string with the supplied indices.

    Args:
        name: The parameter name.
        indices: One or mode multiparm indices.

    Returns:
        The resolved string.
    """
    # Support passing in just a single value.
    if not isinstance(indices, (list, tuple)):
        indices = [indices]

    # Validate that there are at least enough indices for the number of tokens.
    _validate_multiparm_resolve_values(name, indices)

    # Clamp the number of indices to the number of tokens.
    indices = indices[: name.count("#")]

    name_components = name.split("#")

    all_components = []

    for i, j in itertools.zip_longest(name_components, indices, fillvalue=""):
        all_components.extend([i, str(j)])

    return "".join(all_components)


def unexpanded_string_multiparm_instance(
    node: hou.OpNode, name: str, indices: list[int] | int, *, raw_indices: bool = False
) -> tuple[str, ...] | str:
    """Get the unexpanded string of a multiparm parameter by index.

    The name should include the # value which will be replaced by the index.

    The index should be the multiparm index, not including any start offset.

    You cannot try to evaluate a single component of a tuple parameter, evaluate
    the entire tuple instead and get which values you need.

    # String
    >>> eval_multiparm_instance(node, "string#", 1)
    '$HIP'
    # String 2
    >>> eval_multiparm_instance(node, "stringvec#", 1)
    ('$HIP', '$PI')

    Args:
        node: The node to evaluate the parameter on.
        name: The base parameter name.
        indices: The multiparm indices.
        raw_indices: Whether the indices are 'raw'and should not try and take the folder offset into account.

    Returns:
        The evaluated parameter value.

    Raises:
        MissingMultiParmTokenError: If the parameter name does not contain any '#'.
        NoMatchingParameterTemplate: If the parameter name does not exist.
        ParameterIsNotAStringError: If the parameter is not a string.
        InvalidMultiParmIndicesError: If the multiparm index is not valid.
    """
    if "#" not in name:
        raise exceptions.MissingMultiParmTokenError(name)

    ptg = node.parmTemplateGroup()

    parm_template = ptg.find(name)

    if parm_template is None:
        raise exceptions.NoMatchingParameterTemplate(name, node)

    if parm_template.dataType() != hou.parmData.String:
        raise exceptions.ParameterIsNotAStringError(parm_template)

    # Handle directly passing a single index.
    if not isinstance(indices, (list, tuple)):
        indices = [indices]

    if not raw_indices:
        offsets = get_multiparm_container_offsets(name, ptg)

        # Adjust any supplied offsets with the multiparm offset.
        indices = [idx + offset for idx, offset in zip(indices, offsets)]

    # Validate that enough indices were passed.
    _validate_multiparm_resolve_values(name, indices)

    full_name = resolve_multiparm_tokens(name, indices)

    parm_tuple = node.parmTuple(full_name)

    if parm_tuple is None:
        raise exceptions.InvalidMultiParmIndicesError(full_name)

    values = tuple(str(parm.unexpandedString()) for parm in parm_tuple)

    # Return single value for non-tuple parms.
    if len(values) == 1:
        return values[0]

    return values
