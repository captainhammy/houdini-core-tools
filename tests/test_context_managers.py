"""Test the houdini_core_tools.context_managers module."""

# Future
from __future__ import annotations

# Standard Library
from contextlib import nullcontext
from typing import TYPE_CHECKING

# Third Party
import pytest

# Houdini Core Tools
from houdini_core_tools import context_managers, exceptions

# Houdini
import hou

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.usefixtures("load_module_test_hip_file")


# Tests


class Test_emit_varchange:
    """Test houdini_core_tools.context_managers.emit_varchange()."""

    def test_as_with(self, mocker: MockerFixture) -> None:
        """Test using the context manager with the 'with' statement."""
        mock_hscript = mocker.patch("hou.hscript")

        with context_managers.emit_varchange():
            hou.hscript("call a")

            with context_managers.emit_varchange():
                hou.hscript("call b")

            hou.hscript("call c")

        hou.hscript("call d")

        mock_hscript.assert_has_calls((
            mocker.call("call a"),
            mocker.call("call b"),
            mocker.call("call c"),
            mocker.call("varchange"),
            mocker.call("call d"),
        ))

    def test_as_decorator(self, mocker: MockerFixture) -> None:
        """Test using the context manager as a decorator."""
        mock_hscript = mocker.patch("hou.hscript")

        @context_managers.emit_varchange()
        def child() -> None:
            hou.hscript("child a")

        @context_managers.emit_varchange()
        def parent() -> None:
            hou.hscript("parent a")

            child()

            hou.hscript("parent b")

        hou.hscript("call a")

        parent()

        hou.hscript("call b")

        mock_hscript.assert_has_calls((
            mocker.call("call a"),
            mocker.call("parent a"),
            mocker.call("child a"),
            mocker.call("parent b"),
            mocker.call("varchange"),
            mocker.call("call b"),
        ))

    def test_exception_handling(self, mocker: MockerFixture) -> None:
        """Test that varchange is called if an exception happens."""
        mock_hscript = mocker.patch("hou.hscript")

        with pytest.raises(RuntimeError):
            with context_managers.emit_varchange():
                hou.hscript("call a")

                with context_managers.emit_varchange():
                    hou.hscript("call b")
                    raise RuntimeError("An error occurred")

                hou.hscript("call c")

            hou.hscript("call d")

        mock_hscript.assert_has_calls((
            mocker.call("call a"),
            mocker.call("call b"),
            mocker.call("varchange"),
        ))


class Test_temporarily_unlock_parameters:
    """Test houdini_core_tools.context_managers.temporarily_unlock_parameters()."""

    def test_single(self, obj_test_node: hou.ObjNode) -> None:
        """Test for a single parameter."""
        parm = obj_test_node.parm("scale")

        assert parm.isLocked()
        assert parm.eval() == 3

        with context_managers.temporarily_unlock_parameters(parm):
            parm.set(1)

        assert parm.isLocked()
        assert parm.eval() == 1

    def test_single_unlocked(self, obj_test_node: hou.ObjNode) -> None:
        """Test for a single parameter that is not locked."""
        parm = obj_test_node.parm("scale")

        assert not parm.isLocked()
        assert parm.eval() == 3

        with context_managers.temporarily_unlock_parameters(parm):
            parm.set(2)

        assert not parm.isLocked()
        assert parm.eval() == 2

    def test_parm_tuple(self, obj_test_node: hou.ObjNode) -> None:
        """Test with a hou.ParmTuple."""
        parm_tuple = obj_test_node.parmTuple("t")

        for parm in parm_tuple:
            assert parm.isLocked()

        assert parm_tuple.eval() == (1, 2, 3)

        with context_managers.temporarily_unlock_parameters(parm_tuple):
            parm_tuple.set((4, 5, 6))

        for parm in parm_tuple:
            assert parm.isLocked()

        assert parm_tuple.eval() == (4, 5, 6)

    def test_inside_locked(self, obj_test_node: hou.ObjNode) -> None:
        """Test for a parameter inside a locked digital asset."""
        parm = obj_test_node.node("test").parm("scale")

        assert obj_test_node.node("test").isInsideLockedHDA()
        assert parm.isLocked()

        assert parm.eval() == 3

        with (
            pytest.raises(hou.PermissionError, match=f"Error setting lock status for {parm.path()}"),
            context_managers.temporarily_unlock_parameters(parm),
        ):
            parm.set(1)


@pytest.mark.parametrize(
    "category_name, destroy, raiser, expected",
    [
        ("Object", False, nullcontext(), hou.nodeType("Object/subnet")),
        ("Driver", True, nullcontext(), hou.nodeType("Driver/subnet")),
        ("Lop", False, nullcontext(), hou.nodeType("Lop/subnet")),
        ("Shop", True, nullcontext(), hou.nodeType("Shop/material")),
        ("Vop", False, nullcontext(), hou.nodeType("Vop/subnet")),
        ("Cop2", True, nullcontext(), hou.nodeType("CopNet/img")),
        ("Cop", False, nullcontext(), hou.nodeType("CopNet/copnet")),
        ("Sop", True, nullcontext(), hou.nodeType("Object/geo")),
        ("Dop", False, nullcontext(), hou.nodeType("Object/dopnet")),
        ("Top", True, nullcontext(), hou.nodeType("Object/topnet")),
        ("Manager", False, pytest.raises(exceptions.UnsupportedCategoryError), None),
    ],
)
def test_context_container(
    category_name: str,
    destroy: bool,
    raiser: nullcontext | pytest.RaisesExc[exceptions.UnsupportedCategoryError],
    expected: hou.NodeType | None,
) -> None:
    """Test houdini_core_tools.context_managers.context_container()."""
    category = hou.nodeTypeCategories().get(category_name)

    if category is None:
        pytest.skip(f"Category {category_name} not available in {hou.applicationVersionString()}")

    with raiser, context_managers.context_container(category, destroy=destroy) as container:
        assert container.type() == expected

    if expected is not None:
        # If the container was expected to be deleted, trying to access it will result in
        # a hou.ObjectWasDeleted exception, so use that to confirm it was deleted.
        persistence_raiser = pytest.raises(hou.ObjectWasDeleted) if destroy else nullcontext()

        with persistence_raiser:
            assert container.path()


def test_restore_current_selection(obj_test_node: hou.ObjNode) -> None:
    """Test houdini_core_tools.context_managers.restore_current_selection()."""
    node1 = obj_test_node.node("geo1")
    node1.setSelected(True)

    node2 = obj_test_node.node("geo2")
    node2.setSelected(True)

    node3 = obj_test_node.node("geo3")

    assert len(hou.selectedItems()) == 2

    with pytest.raises(RuntimeError), context_managers.restore_current_selection():
        assert not hou.selectedItems()

        node3.setSelected(True)

        assert len(hou.selectedItems()) == 1

        # Throw an exception to test that the 'finally' is executed.
        raise RuntimeError("An error occurred.")

    assert len(hou.selectedItems()) == 2


def test_set_current_node() -> None:
    """Test houdini_core_tools.context_managers.set_current_node()."""
    assert hou.pwd() == hou.node("/")

    with context_managers.set_current_node(hou.node("/obj")):
        assert hou.pwd() == hou.node("/obj")

    assert hou.pwd() == hou.node("/")


def test_set_temporary_update_mode() -> None:
    """Test houdini_core_tools.context_managers.set_temporary_update_mode()."""
    # Ensure the current mode is AutoUpdate.
    hou.setUpdateMode(hou.updateMode.AutoUpdate)
    assert hou.updateModeSetting() == hou.updateMode.AutoUpdate

    with pytest.raises(RuntimeError), context_managers.set_temporary_update_mode(hou.updateMode.Manual):
        # Ensure the mode was set to manual.
        assert hou.updateModeSetting() == hou.updateMode.Manual

        # Throw an exception to test that the 'finally' is executed.
        raise RuntimeError("An error occurred.")

    # Verify that the mode was restored.
    assert hou.updateModeSetting() == hou.updateMode.AutoUpdate
