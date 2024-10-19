"""Test the houdini_core_tools.bounding module."""

# Third Party
import pytest

# Houdini Core Tools
import houdini_core_tools.bounding

# Houdini
import hou

# Tests


@pytest.mark.parametrize(
    "bbox,delta,expected_min",
    ((hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3), hou.Vector3(1, 0.25, 1), hou.Vector3(0, -1.5, -2)),),
)
def test_add_to_bounding_box_min(bbox, delta, expected_min):
    """Test houdini_core_tools.bounding.add_to_bounding_box_min()."""
    houdini_core_tools.bounding.add_to_bounding_box_min(bbox, delta)

    assert bbox.minvec() == expected_min


@pytest.mark.parametrize(
    "bbox,delta,expected_max",
    ((hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3), hou.Vector3(2, 0.25, 1), hou.Vector3(3, 2, 4)),),
)
def test_add_to_bounding_box_max(bbox, delta, expected_max):
    """Test houdini_core_tools.bounding.add_to_bounding_box_max()."""
    houdini_core_tools.bounding.add_to_bounding_box_max(bbox, delta)

    assert bbox.maxvec() == expected_max


@pytest.mark.parametrize("bbox,expected", ((hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3), 80),))
def test_bounding_box_area(bbox, expected):
    """Test houdini_core_tools.bounding.bounding_box_area()."""
    assert houdini_core_tools.bounding.bounding_box_area(bbox) == expected


@pytest.mark.parametrize(
    "bbox, expected",
    [
        (hou.BoundingBox(-1, -1, -1, 1, 1, 1), True),  # Inside
        (hou.BoundingBox(0, 0, 0, 1.5, 1.5, 1.5), False),  # Not inside
        (hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5), False),  # Identical, will fail
    ],
)
def test_bounding_box_is_inside(bbox, expected):
    """Test houdini_core_tools.bounding.bounding_box_is_inside()."""
    test_bbox = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)

    assert houdini_core_tools.bounding.bounding_box_is_inside(test_bbox, bbox) == expected


@pytest.mark.parametrize("bbox,expected", ((hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3), 42),))
def test_bounding_box_volume(bbox, expected):
    """Test houdini_core_tools.bounding.bounding_box_volume()."""
    assert houdini_core_tools.bounding.bounding_box_volume(bbox) == expected


@pytest.mark.parametrize(
    "bbox, expected",
    [
        (hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5), True),
        (hou.BoundingBox(-0.8, -0.85, -0.75, 0.2, 0.15, 0.25), True),
        (hou.BoundingBox(-0.5, -0.5, -0.5, -0.1, -0.1, -0.1), False),
        (hou.BoundingBox(-1.1, -0.85, -0.75, -0.1, 0.15, 0.25), False),
        (hou.BoundingBox(0.2, 0.3, 0.6, 1.2, 1.3, 1.6), False),
        (hou.BoundingBox(-1.2, 0.3, 0.6, -0.2, 1.3, 1.6), False),
        (hou.BoundingBox(-0.358, 0.63, 0.215, 0.642, 1.63, 0.784), False),
    ],
)
def test_bounding_boxes_intersect(bbox, expected):
    """Test houdini_core_tools.bounding.bounding_boxes_intersect()."""
    test_bbox = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

    assert houdini_core_tools.bounding.bounding_boxes_intersect(test_bbox, bbox) == expected
    assert houdini_core_tools.bounding.bounding_boxes_intersect(bbox, test_bbox) == expected


@pytest.mark.parametrize(
    "bbox1,bbox2,expected_vecs",
    (
        (
            hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5),
            hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5),
            (hou.Vector3(), hou.Vector3(0.5, 0.5, 0.5)),
        ),
        (hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5), hou.BoundingBox(-0.5, -0.5, -0.5, -0.1, -0.1, -0.1), None),
    ),
)
def test_compute_bounding_box_intersection(bbox1, bbox2, expected_vecs):
    """Test houdini_core_tools.bounding.compute_bounding_box_intersection()."""
    result = houdini_core_tools.bounding.compute_bounding_box_intersection(bbox1, bbox2)

    if expected_vecs is not None:
        assert result is not None

        assert result.minvec() == expected_vecs[0]
        assert result.maxvec() == expected_vecs[1]

    else:
        assert result is None


@pytest.mark.parametrize(
    "bbox,deltas,expected_vecs",
    (
        (
            hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3),
            (1, 1, 1),
            (hou.Vector3(-2, -2.75, -4), hou.Vector3(2, 2.75, 4)),
        ),
    ),
)
def test_expand_bounding_box(bbox, deltas, expected_vecs):
    """Test houdini_core_tools.bounding.expand_bounding_box()."""
    houdini_core_tools.bounding.expand_bounding_box(bbox, *deltas)

    assert bbox.minvec() == expected_vecs[0]
    assert bbox.maxvec() == expected_vecs[1]
