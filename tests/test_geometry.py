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
    "min_verts,ignore_open,expected",
    (
        (3, True, True),
        (3, False, False),
        (5, True, False),
    ),
)
def test_check_minimum_polygon_vertex_count(obj_test_geo, min_verts, ignore_open, expected):
    """Test houdini_core_tools.geometry.check_minimum_polygon_vertex_count()."""
    assert (
        houdini_core_tools.geometry.check_minimum_polygon_vertex_count(
            obj_test_geo,
            min_verts,
            ignore_open=ignore_open,
        )
        == expected
    )


def test_connected_points(obj_test_geo):
    """Test houdini_core_tools.geometry.connected_points."""
    target = obj_test_geo.globPoints("1 3 5 7")

    points = houdini_core_tools.geometry.connected_points(obj_test_geo.iterPoints()[4])

    assert points == target


@pytest.mark.parametrize(
    "ptnum1,ptnum2,expected",
    (
        (0, 1, True),
        (1, 0, True),
        (0, 2, True),
        (2, 0, True),
        (0, 3, False),
        (3, 0, False),
    ),
)
def test_face_has_edge(obj_test_geo, ptnum1, ptnum2, expected):
    """Test houdini_core_tools.geometry.face_has_edge()."""
    face = obj_test_geo.iterPrims()[0]

    pt0 = obj_test_geo.iterPoints()[ptnum1]
    pt1 = obj_test_geo.iterPoints()[ptnum2]

    assert houdini_core_tools.geometry.face_has_edge(face, pt0, pt1) == expected


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


@pytest.mark.parametrize(
    "node_name,expected",
    (
        ("no_shared", False),
        ("shared", True),
    ),
)
def test_geometry_has_prims_with_shared_vertex_points(obj_test_node, node_name, expected):
    """Test houdini_core_tools.geometry.geometry_has_prims_with_shared_vertex_points()."""
    geometry = obj_test_node.node(node_name).geometry()

    assert houdini_core_tools.geometry.geometry_has_prims_with_shared_vertex_points(geometry) == expected


@pytest.mark.parametrize(
    "node_name,expected",
    (
        ("no_shared", ()),
        ("shared", (81,)),
    ),
)
def test_get_primitives_with_shared_vertex_points(obj_test_node, node_name, expected):
    """Test houdini_core_tools.geometry.get_primitives_with_shared_vertex_points()."""
    geometry = obj_test_node.node(node_name).geometry()
    expected_prims = tuple(geometry.iterPrims()[prim_num] for prim_num in expected)

    result = houdini_core_tools.geometry.get_primitives_with_shared_vertex_points(geometry)

    assert result == expected_prims


def test_num_points(obj_test_geo):
    """Test houdini_core_tools.geometry.num_points."""
    assert houdini_core_tools.geometry.num_points(obj_test_geo) == 5000


# def test_num_prim_vertices(obj_test_geo):
#     """Test houdini_core_tools.geometry.num_prim(vertices()."""
#     assert houdini_core_tools.geometry.num_prim_vertices(obj_test_geo.prims()[0]) == 3


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


def test_primitive_bary_center(obj_test_geo):
    """Test houdini_core_tools.geometry.primitive_bary_center()."""
    target = hou.Vector3(1.5, 1, -1)

    prim = obj_test_geo.iterPrims()[0]

    assert houdini_core_tools.geometry.primitive_bary_center(prim) == target


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


class Test_reverse_prim:
    """Test houdini_core_tools.geometry.reverse_prim()."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        prim = obj_test_geo.iterPrims()[0]

        with pytest.raises(hou.GeometryPermissionError):
            houdini_core_tools.geometry.reverse_prim(prim)

    def test(self, obj_test_geo_copy):
        """Test reversing the vertex order."""
        target = hou.Vector3(0, -1, 0)

        prim = obj_test_geo_copy.iterPrims()[0]
        houdini_core_tools.geometry.reverse_prim(prim)

        assert prim.normal() == target


def test_shared_edges(obj_test_geo):
    """Test houdini_core_tools.geometry.shared_edges()."""
    pr0, pr1 = obj_test_geo.prims()

    edges = houdini_core_tools.geometry.shared_edges(pr0, pr1)

    pt2 = obj_test_geo.iterPoints()[2]
    pt3 = obj_test_geo.iterPoints()[3]

    edge = obj_test_geo.findEdge(pt2, pt3)

    assert edges == (edge,)