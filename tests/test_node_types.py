"""Test the houdini_core_tools.node_types module."""

# Third Party
import pytest

# Houdini Core Tools
import houdini_core_tools.node_types

# Houdini
import hou

pytestmark = pytest.mark.usefixtures("load_module_test_hip_file")


@pytest.mark.parametrize("pass_type", (False, True))
def test_get_node_type_tool(obj_test_node, pass_type):
    """Test houdini_core_tools.node_types.get_node_type_tool()."""
    box = obj_test_node.node("BOX")

    if pass_type:
        box = box.type()

    box_tool = hou.shelves.tools()["sop_box"]
    result = houdini_core_tools.node_types.get_node_type_tool(box)

    assert result == box_tool
