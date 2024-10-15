"""Test the houdini_core_tools.bounding module."""

# Houdini Core Tools
import houdini_core_tools.bounding

# Houdini
import hou

# Tests


def test_bounding_box_area():
    """Test houdini_core_tools.utils.bounding_box_area()."""
    bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)

    assert houdini_core_tools.bounding.bounding_box_area(bbox) == 80


def test_bounding_box_volume():
    """Test houdini_core_tools.utils.bounding_box_volume()."""
    bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)

    assert houdini_core_tools.bounding.bounding_box_volume(bbox) == 42
