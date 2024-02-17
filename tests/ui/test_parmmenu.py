"""Tests for houdini_core_tools.ui.parmmenu module."""

# Third Party
import pytest

# Houdini Core Tools
# Houdini Toolbox
import houdini_core_tools.ui.parmmenu

pytestmark = pytest.mark.usefixtures("load_module_test_hip_file")


# Tests


class Test__valid_to_convert_to_absolute_reference:
    """Test houdini_core_tools.ui.parmmenu._valid_to_convert_to_absolute_reference()."""

    def test_empty_string(self, obj_test_node):
        """Test when the path is an empty string."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_absolute_reference(test_parm)

        assert not result

    def test_not_relative(self, obj_test_node):
        """Test when the path does not seem to be relative."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_absolute_reference(test_parm)

        assert not result

    def test_keyframes(self, obj_test_node):
        """Test when the parameter has keyframes."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_absolute_reference(test_parm)

        assert not result

    def test_can_convert(self, obj_test_node):
        """Test when the path can be converted to an absolute path."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_absolute_reference(test_parm)

        assert result

    def test_invalid_path(self, obj_test_node):
        """Test when the path does not point to a valid node."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_absolute_reference(test_parm)

        assert not result

    def test_expression(self, obj_test_node):
        """Test when the path does not match the unexpanded string (is an expression)."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_absolute_reference(test_parm)

        assert not result

    def test_not_node_reference(self, obj_test_node):
        """Test when the string parameter is not a node reference."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_absolute_reference(test_parm)

        assert not result

    def test_not_string_parm(self, obj_test_node):
        """Test when the string parameter is not a node reference."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_absolute_reference(test_parm)

        assert not result


class Test__valid_to_convert_to_relative_reference:
    """Test houdini_core_tools.ui.parmmenu._valid_to_convert_to_relative_reference()."""

    def test_empty_string(self, obj_test_node):
        """Test when the path is an empty string."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_relative_reference(test_parm)

        assert not result

    def test_not_absolute(self, obj_test_node):
        """Test when the path does not seem to be absolute."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_relative_reference(test_parm)

        assert not result

    def test_keyframes(self, obj_test_node):
        """Test when the parameter has keyframes."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_relative_reference(test_parm)

        assert not result

    def test_can_convert(self, obj_test_node):
        """Test when the path can be converted to an absolute path."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_relative_reference(test_parm)

        assert result

    def test_invalid_path(self, obj_test_node):
        """Test when the path does not point to a valid node."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_relative_reference(test_parm)

        assert not result

    def test_expression(self, obj_test_node):
        """Test when the path does not match the unexpanded string (is an expression)."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_relative_reference(test_parm)

        assert not result

    def test_not_node_reference(self, obj_test_node):
        """Test when the string parameter is not a node reference."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_relative_reference(test_parm)

        assert not result

    def test_not_string_parm(self, obj_test_node):
        """Test when the string parameter is not a node reference."""
        test_parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.ui.parmmenu._valid_to_convert_to_relative_reference(test_parm)

        assert not result


class Test_convert_absolute_to_relative_path_context:
    """Test houdini_core_tools.ui.parmmenu.convert_absolute_to_relative_path_context()."""

    def test_none(self, obj_test_node):
        """Test converting when no parms are suitable to convert."""
        parms = [
            obj_test_node.parm("test_parm1"),
            obj_test_node.parm("test_parm2"),
            obj_test_node.parm("test_parm3"),
        ]
        scriptargs = {"parms": parms}

        result = houdini_core_tools.ui.parmmenu.convert_absolute_to_relative_path_context(scriptargs)

        assert not result

    def test_some(self, obj_test_node):
        """Test converting when at least one parm is suitable to convert."""
        parms = [
            obj_test_node.parm("test_parm1"),
            obj_test_node.parm("test_parm2"),
            obj_test_node.parm("test_parm3"),
        ]
        scriptargs = {"parms": parms}

        result = houdini_core_tools.ui.parmmenu.convert_absolute_to_relative_path_context(scriptargs)

        assert result


def test_convert_absolute_to_relative_path(obj_test_node):
    """Test  houdini_core_tools.ui.parmmenu.convert_absolute_to_relative_path()."""
    parms = [
        obj_test_node.parm("test_parm1"),
        obj_test_node.parm("test_parm2"),
        obj_test_node.parm("test_parm3"),
    ]
    scriptargs = {"parms": parms}

    houdini_core_tools.ui.parmmenu.convert_absolute_to_relative_path(scriptargs)

    assert obj_test_node.evalParm("test_parm1") == "../TEST_NODE"
    assert not obj_test_node.evalParm("test_parm2")
    assert obj_test_node.evalParm("test_parm3") == "../TEST_NODES"


class Test_convert_relative_to_absolute_path_context:
    """Test houdini_core_tools.ui.parmmenu.convert_relative_to_absolute_path_context()."""

    def test_none(self, obj_test_node):
        """Test converting when no parms are suitable to convert."""
        parms = [
            obj_test_node.parm("test_parm1"),
            obj_test_node.parm("test_parm2"),
            obj_test_node.parm("test_parm3"),
        ]
        scriptargs = {"parms": parms}

        result = houdini_core_tools.ui.parmmenu.convert_relative_to_absolute_path_context(scriptargs)

        assert not result

    def test_some(self, obj_test_node):
        """Test converting when at least one parm is suitable to convert."""
        parms = [
            obj_test_node.parm("test_parm1"),
            obj_test_node.parm("test_parm2"),
            obj_test_node.parm("test_parm3"),
        ]
        scriptargs = {"parms": parms}

        result = houdini_core_tools.ui.parmmenu.convert_relative_to_absolute_path_context(scriptargs)

        assert result


def test_convert_relative_to_absolute_path(obj_test_node):
    """Test houdini_core_tools.ui.parmmenu.convert_relative_to_absolute_path."""
    parms = [
        obj_test_node.parm("test_parm1"),
        obj_test_node.parm("test_parm2"),
        obj_test_node.parm("test_parm3"),
    ]
    scriptargs = {"parms": parms}

    houdini_core_tools.ui.parmmenu.convert_relative_to_absolute_path(scriptargs)

    assert obj_test_node.evalParm("test_parm1") == "/obj/TEST_NODE"
    assert not obj_test_node.evalParm("test_parm2")
    assert obj_test_node.evalParm("test_parm3") == "/obj/TEST_NODES"
