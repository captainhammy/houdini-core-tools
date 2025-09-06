"""Functions related to Houdini node types."""

# Houdini
import hou

# Functions


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
