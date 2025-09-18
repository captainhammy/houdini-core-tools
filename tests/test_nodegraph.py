"""Test the houdini_core_tools.nodegraph module."""

# Third Party
import pytest

# Houdini Core Tools
from houdini_core_tools import nodegraph

# Houdini
import nodegraphtitle

# Tests


class TestNodeGraphTitleManager:
    """Test houdini_core_tools.nodegraph.NodeGraphTitleManager."""

    def test___init__(self):
        """Test object initialization."""
        inst = nodegraph.NodeGraphTitleManager()

        assert inst._original_left == nodegraphtitle.networkEditorTitleLeft
        assert inst._original_right == nodegraphtitle.networkEditorTitleRight

        # Test that the class is a singleton.
        inst2 = nodegraph.NodeGraphTitleManager()
        assert inst is inst2

    @pytest.mark.parametrize("has_existing_title", [False, True])
    def test__set_title(self, mocker, has_existing_title):
        """Test NodeGraphTitleManager._set_title()."""
        mgr = nodegraph.NodeGraphTitleManager()

        # Patch the original function to return a known value rather than
        # whatever it wants to calculate.
        mock_func = mocker.MagicMock()
        mock_func.return_value = "Existing" if has_existing_title else ""
        mocker.patch.object(mgr, "_original_left", mock_func)

        def test_func():
            return "this is a title"

        mgr._set_title(
            nodegraph.NodeGraphTitleLocation.LEFT,
            test_func,
        )

        mock_editor = mocker.MagicMock()

        result = nodegraphtitle.networkEditorTitleLeft(mock_editor)

        expected = "this is a title"

        if has_existing_title:
            expected = f"{expected} - Existing"

        assert result == expected

    def test_reset_title(self):
        """Test NodeGraphTitleManager.reset_title()."""
        mgr = nodegraph.NodeGraphTitleManager()

        nodegraphtitle.networkEditorTitleLeft = 5

        mgr.reset_title(nodegraph.NodeGraphTitleLocation.LEFT)

        assert nodegraphtitle.networkEditorTitleLeft == mgr._original_left

    def test_set_dynamic_title(self, mocker):
        """Test NodeGraphTitleManager.set_dynamic_title()."""
        mgr = nodegraph.NodeGraphTitleManager()

        # Patch the original function to return a known value rather than
        # whatever it wants to calculate.
        mock_func = mocker.MagicMock()
        mock_func.return_value = "Existing"
        mocker.patch.object(mgr, "_original_right", mock_func)

        def test_func():
            return "dynamic value"

        mgr.set_dynamic_title(nodegraph.NodeGraphTitleLocation.RIGHT, test_func)

        mock_editor = mocker.MagicMock()

        assert nodegraphtitle.networkEditorTitleRight(mock_editor) == "dynamic value - Existing"

    def test_static_title(self, mocker):
        """Test NodeGraphTitleManager.set_static_title()."""
        mgr = nodegraph.NodeGraphTitleManager()

        # Patch the original function to return a known value rather than
        # whatever it wants to calculate.
        mock_func = mocker.MagicMock()
        mock_func.return_value = "Existing"
        mocker.patch.object(mgr, "_original_right", mock_func)

        mgr.set_static_title(
            nodegraph.NodeGraphTitleLocation.RIGHT,
            "static title",
            include_default=False,
        )

        mock_editor = mocker.MagicMock()

        assert nodegraphtitle.networkEditorTitleRight(mock_editor) == "static title"
