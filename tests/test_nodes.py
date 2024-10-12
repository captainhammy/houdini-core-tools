"""Test the houdini_core_tools.nodes module."""

# Third Party
import pytest

# Houdini Core Tools
import houdini_core_tools.nodes

# Houdini
import hou

pytestmark = pytest.mark.usefixtures("load_module_test_hip_file")


# Tests


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


@pytest.mark.parametrize(
    "node_name,expected_node",
    (
        ("valid", "d/s"),
        ("no_message_nodes", None),
        ("not_otl", None),
    ),
)
def test_get_node_dive_target(obj_test_node, node_name, expected_node):
    """Test houdini_core_tools.nodes.get_node_dive_target()."""
    node = obj_test_node.node(node_name)

    target = node.node(expected_node) if expected_node is not None else None

    assert houdini_core_tools.nodes.get_node_dive_target(node) == target


@pytest.mark.parametrize(
    "node_name,expected_node",
    (
        ("valid", "d/s"),
        ("no_message_nodes", None),
        ("not_otl", None),
    ),
)
def test_get_node_editable_nodes(obj_test_node, node_name, expected_node):
    """Test houdini_core_tools.nodes.get_node_editable_nodes()."""
    node = obj_test_node.node(node_name)

    target = (node.node(expected_node),) if expected_node is not None else ()

    assert houdini_core_tools.nodes.get_node_editable_nodes(node) == target


@pytest.mark.parametrize(
    "node_name,expected_node",
    (
        ("valid", "d/s"),
        ("no_message_nodes", None),
        ("not_otl", None),
    ),
)
def test_get_node_message_nodes(obj_test_node, node_name, expected_node):
    """Test houdini_core_tools.nodes.get_node_message_nodes()."""
    node = obj_test_node.node(node_name)

    target = (node.node(expected_node),) if expected_node is not None else ()

    assert houdini_core_tools.nodes.get_node_message_nodes(node) == target


@pytest.mark.parametrize(
    "node_name,expected_node",
    (
        ("stereo", "stereo_camera"),
        ("stereo/left_camera", None),
        ("stereo/visualization_root", None),
        ("geo/solver", None),
    ),
)
def test_get_node_representative_node(obj_test_node, node_name, expected_node):
    """Test houdini_core_tools.nodes.get_node_representative_node()."""
    node = obj_test_node.node(node_name)

    target = node.node(expected_node) if expected_node is not None else None

    assert houdini_core_tools.nodes.get_node_representative_node(node) == target


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


@pytest.mark.parametrize(
    "node_name,expected",
    (
        ("is_digital_asset", True),
        ("not_digital_asset", False),
    ),
)
def test_is_node_digital_asset(obj_test_node, node_name, expected):
    """Test houdini_core_tools.nodes.is_node_digital_asset()."""
    node = obj_test_node.node(node_name)

    assert houdini_core_tools.nodes.is_node_digital_asset(node) == expected


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
