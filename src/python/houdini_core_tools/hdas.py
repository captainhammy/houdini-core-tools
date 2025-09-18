"""Functions related to Houdini digital assets."""

# Future
from __future__ import annotations

# Standard Library
import pathlib
from typing import TYPE_CHECKING

# Houdini
import hou

if TYPE_CHECKING:
    from collections.abc import Sequence


# Globals
_HOUDINI_INSTALL_DIR = hou.text.expandString("$HFS")
"""The Houdini install location."""


# Non-Public Functions


def _filter_houdini_install_files(file_paths: Sequence[str]) -> tuple[str, ...]:
    """Filter a list of files and remove any files that are in the Houdini install directory ($HFS).

    Args:
        file_paths: The list of file paths to filter.

    Returns:
        The filtered file paths.
    """
    return tuple(file_path for file_path in file_paths if not file_path.startswith(_HOUDINI_INSTALL_DIR))


def _get_node_from_section(node: hou.OpNode, section_name: str) -> hou.OpNode | None:
    """Get a node from an HDA section.

    Args:
        node: A node instance to get a node for.
        section_name: The section name defining the node name relative to the node.

    Returns:
        The found node, if any.
    """
    nodes = _get_nodes_from_section(node, section_name)

    if nodes:
        return nodes[0]

    return None


def _get_nodes_from_section(node: hou.OpNode, section_name: str) -> tuple[hou.OpNode, ...]:
    """Get a tuple of nodes from an HDA section.

    Args:
        node: A node instance to get nodes for.
        section_name: The section name defining the node names relative to the node.

    Returns:
        The found nodes, if any.
    """
    # Get the otl definition for this node's type, if any.
    definition = node.type().definition()

    # Check that there are editable nodes.
    if definition is not None and definition.hasSection(section_name):
        # Extract the list of them.
        contents = definition.sections()[section_name].contents()

        # Glob for any specified nodes and return them.
        return node.glob(contents)

    return ()


# Functions


def get_embedded_asset_definitions() -> tuple[hou.HDADefinition, ...]:
    """Get any digital assets embedded in the hip file.

    Returns:
        Any digital assets embedded in the current hip file.
    """
    try:
        return hou.hda.definitionsInFile("Embedded")

    # An exception raised if there aren't any.
    except hou.OperationFailed:
        return ()


def get_in_use_hda_definitions(*, include_hfs: bool = False) -> tuple[hou.HDADefinition, ...]:
    """Get any digital asset definitions in use in the current session.

    Args:
        include_hfs: Whether to include definitions loaded from the Houdini install directory.

    Returns:
        All in use HDA definitions.
    """
    in_use_paths = get_in_use_hda_files(include_hfs=include_hfs)

    in_use_definitions = []

    for path in in_use_paths:
        definitions = hou.hda.definitionsInFile(path.as_posix())

        in_use_definitions.extend([
            definition for definition in definitions if definition.isCurrent() and definition.nodeType().instances()
        ])

    in_use_definitions.extend(get_embedded_asset_definitions())

    return tuple(in_use_definitions)


def get_in_use_hda_files(*, include_hfs: bool = False) -> tuple[pathlib.Path, ...]:
    """Get all digital asset source files with definitions in use in the session.

    Args:
        include_hfs: Whether to include definitions loaded from the Houdini install directory.

    Returns:
        All in use HDA files.
    """
    in_use_paths = hou.hscript("otinuse -l")[0].split()

    if not include_hfs:
        in_use_paths = _filter_houdini_install_files(in_use_paths)

    return tuple(pathlib.Path(path) for path in in_use_paths if path != "Embedded")


def get_node_descriptive_parameter(node: hou.OpNode) -> hou.Parm | None:
    """Get a node's descriptive parameter, if any.

    Args:
        node: The node to get the descriptive parameter for.

    Returns:
        The node's descriptive parameter, if any.
    """
    definition = node.type().definition()

    # Check that there are editable nodes.
    if definition is None:
        return None

    if definition.hasSection("DescriptiveParmName"):
        return node.parm(definition.sections()["DescriptiveParmName"].contents())

    return None


def get_node_dive_target(node: hou.OpNode) -> hou.OpNode | None:
    """Get this node's dive target node.

    Args:
        node: The node to get the dive target of.

    Returns:
        The node's dive target.
    """
    return _get_node_from_section(node, "DiveTarget")


def get_node_editable_nodes(node: hou.OpNode) -> tuple[hou.OpNode, ...]:
    """Get a list of the node's editable nodes.

    Args:
        node: The node to get the editable nodes for.

    Returns:
        A tuple of editable nodes.
    """
    return _get_nodes_from_section(node, "EditableNodes")


def get_node_guide_geometry_node(node: hou.OpNode) -> hou.OpNode | None:
    """Get a node's guide geometry node.

    Args:
        node: The node to get the guide geometry node for.

    Returns:
        The guide geometry node, if any.
    """
    definition = node.type().definition()

    # Check that there are editable nodes.
    if definition is None:
        return None

    extra_info = definition.extraInfo()

    components = extra_info.split()

    for component in components:
        if component.startswith("guide="):
            guide_path = component[len("guide=") :]
            return node.node(guide_path)

    return None


def get_node_message_nodes(node: hou.OpNode) -> tuple[hou.OpNode, ...]:
    """Get a list of the node's message nodes.

    Args:
        node: The node to get the message nodes for.

    Returns:
        A tuple of message nodes.
    """
    return _get_nodes_from_section(node, "MessageNodes")


def get_node_representative_node(node: hou.OpNode) -> hou.OpNode | None:
    """Get the representative node of this node, if any.

    Args:
        node: The node to get the representative node for.

    Returns:
        The node's representative node.
    """
    # Get the otl definition for this node's type, if any.
    definition = node.type().definition()

    if definition is not None:
        # Get the path to the representative node, if any.
        path = definition.representativeNodePath()

        if path:
            # Return the node.
            return node.node(path)

    return None


def is_digital_asset(node_or_node_type: hou.Node | hou.NodeType) -> bool:
    """Test whether a node or type is a digital asset.

    A node(type) is a digital asset if it has a hou.HDADefinition.

    Args:
        node_or_node_type: A node or node type to test for being a digital asset.

    Returns:
        Whether the node or node type is a digital asset.
    """
    if isinstance(node_or_node_type, hou.Node):
        node_or_node_type = node_or_node_type.type()

    return node_or_node_type.definition() is not None
