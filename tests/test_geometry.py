"""Test the houdini_core_tools.geometry module."""

# Standard Library
from contextlib import nullcontext

# Third Party
import pytest

# Houdini Core Tools
import houdini_core_tools.geometry
from houdini_core_tools import exceptions

# Houdini
import hou

pytestmark = pytest.mark.usefixtures("load_module_test_hip_file")


# Tests


@pytest.mark.parametrize(
    "attrib_type,name,ctx",
    (
        (hou.attribType.Vertex, "vertex_attrib", nullcontext()),
        (hou.attribType.Point, "point_attrib", nullcontext()),
        (hou.attribType.Prim, "prim_attrib", nullcontext()),
        (hou.attribType.Global, "global_attrib", nullcontext()),
        (None, "bad", pytest.raises(exceptions.UnexpectedAttributeTypeError)),
    ),
)
def test_find_attrib(obj_test_geo, attrib_type, name, ctx):
    """Test houdini_core_tools.geometry.find_attrib()."""
    with ctx:
        result = houdini_core_tools.geometry.find_attrib(obj_test_geo, attrib_type, name)

        assert isinstance(result, hou.Attrib)
        assert result.name() == name
        assert result.type() == attrib_type


@pytest.mark.parametrize(
    "detail1,detail2,expected",
    (
        ("detail1", "detail2", True),
        ("detail1", "detail3", False),
        ("detail2", "detail3", False),
    ),
)
def test_geo_details_match(obj_test_node, detail1, detail2, expected):
    """Test houdini_core_tools.geometry.geo_details_match()."""
    geo1 = obj_test_node.node(detail1).geometry()
    geo2 = obj_test_node.node(detail2).geometry()

    assert houdini_core_tools.geometry.geo_details_match(geo1, geo2) is expected


@pytest.mark.parametrize(
    "points_list,expected",
    (
        ([], ()),
        ([0, 1, 2, 4], (0, 1, 2)),
    ),
)
def test_get_points_from_list(obj_test_geo, points_list, expected):
    """Test houdini_core_tools.geometry.get_points_from_list()."""
    result = houdini_core_tools.geometry.get_points_from_list(obj_test_geo, points_list)

    num_points = len(obj_test_geo.iterPoints())

    expected_points = tuple(obj_test_geo.iterPoints()[idx] for idx in expected if idx < num_points)

    assert result == expected_points


@pytest.mark.parametrize(
    "prims_list,expected",
    (
        ([], ()),
        ([0, 1, 2, 4], (0, 1, 2)),
    ),
)
def test_get_prims_from_list(obj_test_geo, prims_list, expected):
    """Test houdini_core_tools.geometry.get_prims_from_list()."""
    result = houdini_core_tools.geometry.get_prims_from_list(obj_test_geo, prims_list)

    num_prims = len(obj_test_geo.iterPrims())

    expected_prims = tuple(obj_test_geo.iterPrims()[idx] for idx in expected if idx < num_prims)

    assert result == expected_prims


def test_num_points(obj_test_geo):
    """Test houdini_core_tools.geometry.num_points."""
    assert houdini_core_tools.geometry.num_points(obj_test_geo) == 5000


def test_num_prim_vertices(obj_test_geo):
    """Test houdini_core_tools.geometry.num_prim(vertices()."""
    assert houdini_core_tools.geometry.num_prim_vertices(obj_test_geo.prims()[0]) == 3


def test_num_prims(obj_test_geo):
    """Test houdini_core_tools.geometry.num_prims()."""
    assert houdini_core_tools.geometry.num_prims(obj_test_geo) == 12


def test_num_vertices(obj_test_geo):
    """Test houdini_core_tools.geometry.num_vertices()."""
    assert houdini_core_tools.geometry.num_vertices(obj_test_geo) == 48


def test_primitive_area(obj_test_geo):
    """Test houdini_core_tools.geometry.primitive_area()."""
    target = 4.375
    prim = obj_test_geo.iterPrims()[0]

    assert houdini_core_tools.geometry.primitive_area(prim) == target


def test_primitive_bounding_box(obj_test_geo):
    """Test houdini_core_tools.geometry.primitive_bounding_box()."""
    target = hou.BoundingBox(-0.75, 0, -0.875, 0.75, 1.5, 0.875)

    prim = obj_test_geo.iterPrims()[0]

    assert houdini_core_tools.geometry.primitive_bounding_box(prim) == target


def test_primitive_perimeter(obj_test_geo):
    """Test houdini_core_tools.geometry.primitive_perimeter()."""
    target = 6.5

    prim = obj_test_geo.iterPrims()[0]

    assert houdini_core_tools.geometry.primitive_perimeter(prim) == target


def test_primitive_volume(obj_test_geo):
    """Test houdini_core_tools.geometry.primitive_volume()."""
    target = 0.1666666716337204

    prim = obj_test_geo.iterPrims()[0]

    assert hou.almostEqual(houdini_core_tools.geometry.primitive_volume(prim), target)
