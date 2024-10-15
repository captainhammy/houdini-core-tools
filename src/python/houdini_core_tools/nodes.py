"""Functions related to Houdini nodes."""

# Future
from __future__ import annotations

# Standard Library
import json
from typing import TYPE_CHECKING, Any

# Houdini
import hou

if TYPE_CHECKING:
    from collections.abc import Sequence


# Functions


def disconnect_all_inputs(node: hou.Node) -> None:
    """Disconnect all the node's inputs.

    Args:
        node: The node to disconnect all inputs for.
    """
    connections = node.inputConnections()

    with hou.undos.group("Disconnect inputs"):
        for connection in reversed(connections):
            node.setInput(connection.inputIndex(), None)


def disconnect_all_outputs(node: hou.Node) -> None:
    """Disconnect all of this node's outputs.

    Args:
        node: The node to disconnect all outputs for.
    """
    connections = node.outputConnections()

    with hou.undos.group("Disconnect outputs"):
        for connection in connections:
            connection.outputNode().setInput(connection.inputIndex(), None)


def get_node_author(node: hou.OpNode) -> str:
    """Get the name of the node creator.

    Args:
        node: The node to get the author of.

    Returns:
        The author name.
    """
    return hou.hscript(f"opls -l {node.path()}")[0].strip().split()[-2]


def get_node_message_nodes(node: hou.OpNode) -> tuple[hou.OpNode, ...]:
    """Get a list of the node's message nodes.

    Args:
        node: The node to get the message nodes for.

    Returns:
        A tuple of message nodes.
    """
    # Get the otl definition for this node's type, if any.
    definition = node.type().definition()

    # Check that there are message nodes.
    if definition is not None and "MessageNodes" in definition.sections():
        # Extract the list of them.
        contents = definition.sections()["MessageNodes"].contents()

        # Glob for any specified nodes and return them.
        return node.glob(contents)

    return ()


def get_node_editable_nodes(node: hou.OpNode) -> tuple[hou.OpNode, ...]:
    """Get a list of the node's editable nodes.

    Args:
        node: The node to get the editable nodes for.

    Returns:
        A tuple of editable nodes.
    """
    # Get the otl definition for this node's type, if any.
    definition = node.type().definition()

    # Check that there are editable nodes.
    if definition is not None and "EditableNodes" in definition.sections():
        # Extract the list of them.
        contents = definition.sections()["EditableNodes"].contents()

        # Glob for any specified nodes and return them.
        return node.glob(contents)

    return ()


def get_node_dive_target(node: hou.OpNode) -> hou.OpNode | None:
    """Get this node's dive target node.

    Args:
        node: The node to get the dive target of.

    Returns:
        The node's dive target.
    """
    # Get the otl definition for this node's type, if any.
    definition = node.type().definition()

    # Check that there is a dive target.
    if definition is not None and "DiveTarget" in definition.sections():
        # Get its path.
        target = definition.sections()["DiveTarget"].contents()

        # Return the node.
        return node.node(target)

    return None


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


def get_nodes_from_paths(paths: Sequence[str]) -> tuple[hou.Node, ...]:
    """Convert a list of string paths to hou.Node objects.

    Args:
        paths: A list of paths.

    Returns:
        A tuple of hou.Node objects.
    """
    return tuple(hou.node(path) for path in paths if path)


def get_node_type_tool(node_or_node_type: hou.Node | hou.NodeType) -> hou.Tool | None:
    """Get the hou.Tool entry for a particular node or node type.

    Args:
        node_or_node_type: The node or node type to get the tool for.

    Returns:
        The node type tool, if any.
    """
    # Get the node type if the argument was a node.
    if isinstance(node_or_node_type, hou.Node):
        node_or_node_type = node_or_node_type.type()

    # Get the list of all installed tools.
    tools = hou.shelves.tools()

    # Build a tool name string.  Tool names are defined as
    # OperatorTable_OperatorName. (i.e. sop_sphere, object_geo).
    tool_name = f"{node_or_node_type.category().name().lower()}_{node_or_node_type.name()}"

    return tools.get(tool_name)


def is_node_digital_asset(node: hou.OpNode) -> bool:
    """Determine if this node is a digital asset.

    A node is a digital asset if its node type has a hou.HDADefinition.

    Args:
        node: The node to check for being a digital asset.

    Returns:
        Whether this node is a digital asset.
    """
    return node.type().definition() is not None


def node_is_contained_by(node: hou.Node, containing_node: hou.Node) -> bool:
    """Test if a node is a contained within another node.

    Args:
        node: The node to check for being contained.
        containing_node: A node which may contain this node

    Returns:
        Whether this node is a child of the passed node.
    """
    # Get this node's parent.
    parent = node.parent()

    # Keep looking until we have no more parents.
    while parent is not None:
        # If the parent is the target node, return True.
        if parent == containing_node:
            return True

        # Get the parent's parent and try again.
        parent = parent.parent()

    # Didn't find the node, so return False.
    return False


def read_from_user_data(node: hou.Node, user_data_name: str) -> Any:
    """Read a data structure stored in a node's user data dictionary.

    Use this in conjunction with `store_as_user_data`.

    Args:
        node: The node the data is stored on.
        user_data_name: The user data key the data is stored under.

    Returns:
        The stored data.
    """
    return json.loads(node.userData(user_data_name))


def store_as_user_data(node: hou.Node, user_data_name: str, data: Any) -> None:
    """Store a data structure in a node's user data dictionary.

    Use this in conjunction with `read_from_user_data`.

    The structure to be stored must be encodable by json.

    Args:
        node: The node to store the data on.
        user_data_name: The user data key to store the data under.
        data: The data to store.
    """
    node.setUserData(user_data_name, json.dumps(data))
