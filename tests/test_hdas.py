"""Test the houdini_core_tools.hdas module."""

# Standard Library
import pathlib

# Third Party
import pytest

# Houdini Core Tools
import houdini_core_tools.hdas

# Houdini
import hou

pytestmark = pytest.mark.usefixtures("load_module_test_hip_file")


# Tests


def test__filter_houdini_install_files():
    """Test houdini_core_tools.hdas._filter_houdini_install_files()."""
    loaded_files = hou.hda.loadedFiles()
    assert any(hda_file.startswith(houdini_core_tools.hdas._HOUDINI_INSTALL_DIR) for hda_file in loaded_files)

    results = houdini_core_tools.hdas._filter_houdini_install_files(loaded_files)

    assert not any(result.startswith(houdini_core_tools.hdas._HOUDINI_INSTALL_DIR) for result in results)


@pytest.mark.parametrize(
    "raise_exception",
    (False, True),
)
def test_get_embedded_asset_definitions(mocker, raise_exception):
    """Test houdini_core_tools.hdas.get_embedded_asset_definitions()."""
    if raise_exception:
        mocker.patch("hou.hda.definitionsInFile", side_effect=hou.OperationFailed)

    result = houdini_core_tools.hdas.get_embedded_asset_definitions()

    expected = () if raise_exception else hou.hda.definitionsInFile("Embedded")

    assert result == expected


@pytest.mark.parametrize(
    "include_hfs,expected_count",
    (
        (False, 5),
        (True, 10),
    ),
)
def test_get_in_use_hda_definitions(include_hfs, expected_count):
    """Test houdini_core_tools.hdas.get_in_use_hda_definitions()."""
    result = houdini_core_tools.hdas.get_in_use_hda_definitions(include_hfs=include_hfs)
    assert len(result) == expected_count

    if result:
        assert all(isinstance(definition, hou.HDADefinition) for definition in result)


@pytest.mark.parametrize(
    "include_hfs,expected_count",
    (
        (False, 1),  # Only 1 HDA that is not HFS or embedded is being used.
        (True, 6),  # There are 5 HFS HDAs + the other external ref.
    ),
)
def test_get_in_use_hda_files(include_hfs, expected_count):
    """Test houdini_core_tools.hdas.get_in_use_hda_files()."""
    result = houdini_core_tools.hdas.get_in_use_hda_files(include_hfs=include_hfs)
    assert len(result) == expected_count

    if result:
        assert all(isinstance(path, pathlib.Path) for path in result)


@pytest.mark.parametrize(
    "node_name,expected_parm",
    (
        ("valid", "descriptive_parm"),
        ("no_descriptive", None),
        ("not_otl", None),
    ),
)
def test_get_node_descriptive_parameter(obj_test_node, node_name, expected_parm):
    """Test houdini_core_tools.hdas.get_node_descriptive_parameter()."""
    node = obj_test_node.node(node_name)

    target = node.parm(expected_parm) if expected_parm is not None else None

    assert houdini_core_tools.hdas.get_node_descriptive_parameter(node) == target


@pytest.mark.parametrize(
    "node_name,expected_node",
    (
        ("valid", "d/s"),
        ("no_message_nodes", None),
        ("not_otl", None),
    ),
)
def test_get_node_dive_target(obj_test_node, node_name, expected_node):
    """Test houdini_core_tools.hdas.get_node_dive_target()."""
    node = obj_test_node.node(node_name)

    target = node.node(expected_node) if expected_node is not None else None

    assert houdini_core_tools.hdas.get_node_dive_target(node) == target


@pytest.mark.parametrize(
    "node_name,expected_node",
    (
        ("valid", "d/s"),
        ("no_message_nodes", None),
        ("not_otl", None),
    ),
)
def test_get_node_editable_nodes(obj_test_node, node_name, expected_node):
    """Test houdini_core_tools.hdas.get_node_editable_nodes()."""
    node = obj_test_node.node(node_name)

    target = (node.node(expected_node),) if expected_node is not None else ()

    assert houdini_core_tools.hdas.get_node_editable_nodes(node) == target


@pytest.mark.parametrize(
    "node_name,expected_node",
    (
        ("has_guide", "GUIDE_NODE"),
        ("bad_guide_node", None),
        ("no_guides", None),
        ("not_otl", None),
    ),
)
def test_get_node_guide_geometry_node(obj_test_node, node_name, expected_node):
    """Test houdini_core_tools.hdas.get_node_guide_geometry_node()."""
    node = obj_test_node.node(node_name)

    target = node.node(expected_node) if expected_node is not None else None

    assert houdini_core_tools.hdas.get_node_guide_geometry_node(node) == target


@pytest.mark.parametrize(
    "node_name,expected_node",
    (
        ("valid", "d/s"),
        ("no_message_nodes", None),
        ("not_otl", None),
    ),
)
def test_get_node_message_nodes(obj_test_node, node_name, expected_node):
    """Test houdini_core_tools.hdas.get_node_message_nodes()."""
    node = obj_test_node.node(node_name)

    target = (node.node(expected_node),) if expected_node is not None else ()

    assert houdini_core_tools.hdas.get_node_message_nodes(node) == target


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
    """Test houdini_core_tools.hdas.get_node_representative_node()."""
    node = obj_test_node.node(node_name)

    target = node.node(expected_node) if expected_node is not None else None

    assert houdini_core_tools.hdas.get_node_representative_node(node) == target


@pytest.mark.parametrize(
    "node_name,expected",
    (
        ("is_digital_asset", True),
        ("not_digital_asset", False),
    ),
)
def test_is_digital_asset(obj_test_node, node_name, expected):
    """Test houdini_core_tools.hdas.is_digital_asset()."""
    node = obj_test_node.node(node_name)

    assert houdini_core_tools.hdas.is_digital_asset(node) == expected
    assert houdini_core_tools.hdas.is_digital_asset(node.type()) == expected
