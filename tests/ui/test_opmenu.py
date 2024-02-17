"""Tests for houdini_core_tools.ui.opmenu module."""

# Third Party
import pytest

# Houdini Core Tools
import houdini_core_tools.ui.opmenu

pytestmark = pytest.mark.usefixtures("load_module_test_hip_file")


# Tests


def test_create_absolute_reference_copy(obj_test_node):
    """Test houdini_core_tools.ui.opmenu.create_absolute_reference_copy()."""
    scriptargs = {"node": obj_test_node}

    result = houdini_core_tools.ui.opmenu.create_absolute_reference_copy(scriptargs)

    assert result.evalParm("scale") == 3

    assert result.parm("scale").expression() == f'ch("{obj_test_node.path()}/scale")'


def test_unlock_parents(obj_test_node):
    """Test houdini_core_tools.ui.opmenu.unlock_parents()."""
    test_node = obj_test_node.node("unlock_parents_inner_container/TEST")

    scriptargs = {"node": test_node}

    assert obj_test_node.matchesCurrentDefinition()
    assert test_node.parent().matchesCurrentDefinition()

    houdini_core_tools.ui.opmenu.unlock_parents(scriptargs)

    assert not test_node.isInsideLockedHDA()


def test_unlock_parents_context(obj_test_node):
    """Test houdini_core_tools.ui.opmenu.unlock_parents_context()."""
    test_node = obj_test_node.node("locked/unlock_parents_inner_container")

    assert houdini_core_tools.ui.opmenu.unlock_parents_context({"node": test_node})

    test_node = obj_test_node.node("unlocked/unlock_parents_inner_container")

    assert not houdini_core_tools.ui.opmenu.unlock_parents_context({"node": test_node})
