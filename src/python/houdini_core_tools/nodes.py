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


def get_containing_node(node: hou.Node) -> hou.Node | None:
    """Returns the nearest parent node which is of a different node type category.

    Args:
        node: The node to find the containing node of.

    Returns:
        The containing node.
    """
    parent = node.parent()

    while parent is not None:
        parent_type = parent.type()
        parent_category = parent_type.category()

        # If the parent node is the root node, /, then an exception
        # will be thrown so we need to account for it.
        try:
            parent_child_type = parent_type.childTypeCategory()

        except hou.OperationFailed:
            parent_child_type = None

        if parent_category != parent_child_type:
            return parent

        parent = parent.parent()

    return None


def get_node_author(node: hou.OpNode) -> str:
    """Get the name of the node creator.

    Args:
        node: The node to get the author of.

    Returns:
        The author name.
    """
    return hou.hscript(f"opls -d -l {node.path()}")[0].strip().split()[-2]


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
