"""Test the houdini_core_tools.nodes module."""

# Third Party
import pytest

# Houdini Core Tools
import houdini_core_tools.nodes

# Houdini
import hou

pytestmark = pytest.mark.usefixtures("load_module_test_hip_file")


# Tests


@pytest.mark.parametrize(
    "name,expected_path",
    (
        ("/", None),
        ("/obj", "/"),
        ("geo_container/box", "geo_container"),
        ("geo_container/inner/sphere", "geo_container"),
        ("lopnet/subnet/file", "lopnet"),
        ("chopnet/lopnet/subnet/file", "chopnet/lopnet"),
    ),
)
def test_get_containing_node(obj_test_node, name, expected_path):
    """Test houdini_core_tools.nodes.get_containing_node()."""
    node = obj_test_node.node(name)

    expected = obj_test_node.node(expected_path) if expected_path else None

    result = houdini_core_tools.nodes.get_containing_node(node)
    assert result == expected


def test_disconnect_all_inputs(obj_test_node):
    """Test houdini_core_tools.nodes.disconnect_all_outputs()."""
    node = obj_test_node.node("merge")

    houdini_core_tools.nodes.disconnect_all_inputs(node)

    assert not node.inputs()


def test_disconnect_all_outputs(obj_test_node):
    """Test houdini_core_tools.nodes.disconnect_all_inputs()."""
    node = obj_test_node.node("file")

    houdini_core_tools.nodes.disconnect_all_outputs(node)

    assert not node.outputs()


def test_get_node_author(obj_test_node):
    """Test houdini_core_tools.nodes.get_node_author()."""
    assert houdini_core_tools.nodes.get_node_author(obj_test_node) == "grahamt"


@pytest.mark.parametrize("pass_type", (False, True))
def test_get_node_type_tool(obj_test_node, pass_type):
    """Test houdini_core_tools.nodes.get_node_type_tool()."""
    box = obj_test_node.node("BOX")

    if pass_type:
        box = box.type()

    box_tool = hou.shelves.tools()["sop_box"]
    result = houdini_core_tools.nodes.get_node_type_tool(box)

    assert result == box_tool


def test_get_nodes_from_paths(obj_test_node):
    """Test houdini_core_tools.nodes.get_nodes_from_paths()."""
    paths = (
        "/obj/test_get_nodes_from_paths/null1",
        "",
        "/obj/test_get_nodes_from_paths/null3",
    )

    expected = (
        obj_test_node.node("null1"),
        obj_test_node.node("null3"),
    )

    result = houdini_core_tools.nodes.get_nodes_from_paths(paths)

    assert result == expected


def test_node_is_contained_by(obj_test_node):
    """Test houdini_core_tools.nodes.node_is_contained_by()."""
    box = obj_test_node.node("subnet/box")

    assert houdini_core_tools.nodes.node_is_contained_by(box, obj_test_node)
    assert not houdini_core_tools.nodes.node_is_contained_by(obj_test_node, hou.node("/shop"))


def test_read_from_user_data(obj_test_node):
    """Test houdini_core_tools.nodes.read_from_user_data()."""
    expected = {"a": 1, "b": {"zz": "aa"}, "c": 123}

    result = houdini_core_tools.nodes.read_from_user_data(obj_test_node, "test_key")

    assert result == expected


def test_store_as_user_data(obj_test_node):
    """Test houdini_core_tools.nodes.store_as_user_data()."""
    test_data = {"a": 1, "b": {"zz": "aa"}, "c": 123}

    houdini_core_tools.nodes.store_as_user_data(obj_test_node, "test_key", test_data)

    assert obj_test_node.userData("test_key") == '{"a": 1, "b": {"zz": "aa"}, "c": 123}'
