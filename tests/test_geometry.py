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
    "attrib_type,attrib_name,context,expected",
    (
        (hou.attribType.Point, "test_point", nullcontext(), tuple(["value"] * 12)),
        (hou.attribType.Prim, "test", nullcontext(), tuple(["value"] * 5)),
        (hou.attribType.Vertex, "test_vertex", nullcontext(), tuple(["value"] * 20)),
        (hou.attribType.Global, "test_detail", pytest.raises(exceptions.InvalidAttributeTypeError), None),
    ),
)
def test__set_all_shared_values(obj_test_geo_copy, attrib_type, attrib_name, context, expected):
    """Test houdini_core_tools.geometry._set_all_shared_values()."""
    attrib = houdini_core_tools.geometry.find_attrib(obj_test_geo_copy, attrib_type, attrib_name)

    with context:
        houdini_core_tools.geometry._set_all_shared_values(
            attrib,
            "value",
        )

        match attrib_type:
            case hou.attribType.Point:
                assert obj_test_geo_copy.pointStringAttribValues(attrib_name) == expected

            case hou.attribType.Prim:
                assert obj_test_geo_copy.primStringAttribValues(attrib_name) == expected

            case hou.attribType.Vertex:
                assert obj_test_geo_copy.vertexStringAttribValues(attrib_name) == expected


@pytest.mark.parametrize(
    "attrib_type,attrib_name,context,group_type,group_name,expected",
    (
        (
            hou.attribType.Point,
            "test_point",
            nullcontext(),
            hou.PointGroup,
            "point_group",
            tuple(["value"] * 5 + [""] * 7),
        ),
        (
            hou.attribType.Point,
            "test_point",
            pytest.raises(exceptions.InvalidGroupTypeError),
            hou.PrimGroup,
            "prim_group",
            None,
        ),
        (hou.attribType.Prim, "test", nullcontext(), hou.PrimGroup, "prim_group", tuple(["value"] * 3 + [""] * 2)),
        (
            hou.attribType.Prim,
            "test",
            pytest.raises(exceptions.InvalidGroupTypeError),
            hou.PointGroup,
            "point_group",
            None,
        ),
        (
            hou.attribType.Vertex,
            "test_vertex",
            nullcontext(),
            hou.VertexGroup,
            "vertex_group",
            tuple([""] * 10 + ["value"] * 10),
        ),
        (
            hou.attribType.Vertex,
            "test_vertex",
            pytest.raises(exceptions.InvalidGroupTypeError),
            hou.PrimGroup,
            "prim_group",
            None,
        ),
        (hou.attribType.Global, "test_detail", pytest.raises(exceptions.InvalidAttributeTypeError), None, None, None),
    ),
)
def test__set_group_shared_values(
    obj_test_geo_copy, attrib_type, attrib_name, context, group_type, group_name, expected
):
    """Test houdini_core_tools.geometry._set_group_shared_values()."""
    attrib = houdini_core_tools.geometry.find_attrib(obj_test_geo_copy, attrib_type, attrib_name)
    group = houdini_core_tools.geometry.find_group(obj_test_geo_copy, group_type, group_name) if group_name else None

    with context:
        houdini_core_tools.geometry._set_group_shared_values(
            attrib,
            group,
            "value",
        )

        match attrib_type:
            case hou.attribType.Point:
                assert obj_test_geo_copy.pointStringAttribValues(attrib_name) == expected

            case hou.attribType.Prim:
                assert obj_test_geo_copy.primStringAttribValues(attrib_name) == expected

            case hou.attribType.Vertex:
                assert obj_test_geo_copy.vertexStringAttribValues(attrib_name) == expected


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


@pytest.mark.parametrize("pt_num,expected", ((4, (1, 3, 5, 7)),))
def test_connected_points(obj_test_geo, pt_num, expected):
    """Test houdini_core_tools.geometry.connected_points."""
    target = obj_test_geo.globPoints(" ".join(str(ptnum) for ptnum in expected))

    points = houdini_core_tools.geometry.connected_points(obj_test_geo.iterPoints()[pt_num])

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
    "group_type,name,ctx",
    (
        (hou.VertexGroup, "vertex_group", nullcontext()),
        (hou.PointGroup, "point_group", nullcontext()),
        (hou.PrimGroup, "prim_group", nullcontext()),
        (hou.EdgeGroup, "edge_group", nullcontext()),
        (hou.Attrib, "bad", pytest.raises(exceptions.UnexpectedGroupTypeError)),
    ),
)
def test_find_group(obj_test_geo, group_type, name, ctx):
    """Test houdini_core_tools.geometry.find_group()."""
    with ctx:
        result = houdini_core_tools.geometry.find_group(obj_test_geo, group_type, name)

        assert isinstance(result, group_type)
        assert result.name() == name


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
    "node_name,context,expected",
    (
        ("RAW", pytest.raises(exceptions.PrimitiveIsRawGeometryError), None),
        (
            "XFORMED",
            nullcontext(),
            hou.Matrix4((
                (0.6819891929626465, -0.7313622236251831, 0.0, 0.0),
                (0.48333778977394104, 0.4507084786891937, -0.7504974603652954, 0.0),
                (0.5488855242729187, 0.5118311643600464, 0.660873293876648, 0.0),
                (0.3173518180847168, 0.38005995750427246, -0.6276679039001465, 1.0),
            )),
        ),
        (
            "SINGLE_POINT",
            nullcontext(),
            hou.Matrix4((
                (-0.42511632340174754, 0.8177546905539287, -0.38801208441803603, 0.0),
                (-0.3819913447800112, 0.2265424934082094, 0.895969369562124, 0.0),
                (0.8205843796286518, 0.5291084621865726, 0.21606830205289468, 0.0),
                (0.0, 0.0, 0.0, 1.0),
            )),
        ),
    ),
)
def test_get_oriented_point_transform(obj_test_node, node_name, context, expected):
    """Test houdini_core_tools.geometry.get_oriented_point_transform()."""
    geo = obj_test_node.node(node_name).geometry()
    pt = geo.points()[0]

    with context:
        result = houdini_core_tools.geometry.get_oriented_point_transform(pt)

        assert result.isAlmostEqual(expected)


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


class Test_group_bounding_box:
    """Test houdini_core_tools.geometry.group_bounding_box()."""

    def test_point_group(self, obj_test_geo):
        """Test getting the bounding box from a point group."""
        target = hou.BoundingBox(-4, 0, -1, -2, 0, 2)

        group = obj_test_geo.pointGroups()[0]
        bbox = houdini_core_tools.geometry.group_bounding_box(group)

        assert bbox == target

    def test_prim_group(self, obj_test_geo):
        """Test getting the bounding box from a prim group."""
        target = hou.BoundingBox(-5, 0, -4, 4, 0, 5)

        group = obj_test_geo.primGroups()[0]
        bbox = houdini_core_tools.geometry.group_bounding_box(group)

        assert bbox == target

    def test_edge_group(self, obj_test_geo):
        """Test getting the bounding box from an edge group."""
        target = hou.BoundingBox(-5, 0, -5, 4, 0, 5)

        group = obj_test_geo.edgeGroups()[0]
        bbox = houdini_core_tools.geometry.group_bounding_box(group)

        assert bbox == target

    def test_invalid(self):
        """Test an invalid argument."""
        with pytest.raises(exceptions.UnexpectedGroupTypeError):
            houdini_core_tools.geometry.group_bounding_box(hou.Vector3())


def test_num_points(obj_test_geo):
    """Test houdini_core_tools.geometry.num_points."""
    assert houdini_core_tools.geometry.num_points(obj_test_geo) == 5000


def test_num_prims(obj_test_geo):
    """Test houdini_core_tools.geometry.num_prims()."""
    assert houdini_core_tools.geometry.num_prims(obj_test_geo) == 12


def test_num_vertices(obj_test_geo):
    """Test houdini_core_tools.geometry.num_vertices()."""
    assert houdini_core_tools.geometry.num_vertices(obj_test_geo) == 48


@pytest.mark.parametrize(
    "node_name",
    (
        "v_N_up",
        "v_up",
        "pscale_scale",
        "trans_rot_pivot",
        "orient",
    ),
)
def test_point_instance_transform(obj_test_node, node_name):
    """Test houdini_core_tools.geometry.point_instance_transform()."""
    geometry = obj_test_node.node(node_name).geometry()
    pt = geometry.points()[0]

    expected_geo = obj_test_node.node(f"{node_name}_EXPECTED").geometry()
    prim_transform = expected_geo.prims()[0].fullTransform()

    result = houdini_core_tools.geometry.point_instance_transform(pt)

    assert result.isAlmostEqual(prim_transform)


@pytest.mark.parametrize("prim_num,expected", ((0, 4.375),))
def test_primitive_area(obj_test_geo, prim_num, expected):
    """Test houdini_core_tools.geometry.primitive_area()."""
    prim = obj_test_geo.iterPrims()[prim_num]

    assert houdini_core_tools.geometry.primitive_area(prim) == expected


@pytest.mark.parametrize("prim_num,expected", ((0, hou.Vector3(1.5, 1, -1)),))
def test_primitive_bary_center(obj_test_geo, prim_num, expected):
    """Test houdini_core_tools.geometry.primitive_bary_center()."""
    prim = obj_test_geo.iterPrims()[prim_num]

    assert houdini_core_tools.geometry.primitive_bary_center(prim) == expected


@pytest.mark.parametrize("prim_num,expected", ((0, hou.BoundingBox(-0.75, 0, -0.875, 0.75, 1.5, 0.875)),))
def test_primitive_bounding_box(obj_test_geo, prim_num, expected):
    """Test houdini_core_tools.geometry.primitive_bounding_box()."""
    prim = obj_test_geo.iterPrims()[prim_num]

    assert houdini_core_tools.geometry.primitive_bounding_box(prim) == expected


@pytest.mark.parametrize("prim_num,expected", ((0, 6.5),))
def test_primitive_perimeter(obj_test_geo, prim_num, expected):
    """Test houdini_core_tools.geometry.primitive_perimeter()."""
    prim = obj_test_geo.iterPrims()[prim_num]

    assert houdini_core_tools.geometry.primitive_perimeter(prim) == expected


@pytest.mark.parametrize("prim_num,expected", ((0, 0.1666666716337204),))
def test_primitive_volume(obj_test_geo, prim_num, expected):
    """Test houdini_core_tools.geometry.primitive_volume()."""
    prim = obj_test_geo.iterPrims()[prim_num]

    assert hou.almostEqual(houdini_core_tools.geometry.primitive_volume(prim), expected)


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


@pytest.mark.parametrize(
    "attrib_name,context,group_name",
    (
        (
            "not_string_point",
            pytest.raises(exceptions.AttributeNotAStringError),
            None,
        ),
        (
            "test_point",
            nullcontext(),
            None,
        ),
        (
            "test_point",
            nullcontext(),
            "point_group",
        ),
    ),
)
def test_set_shared_string_attrib(mocker, obj_test_geo_copy, attrib_name, context, group_name):
    """Test houdini_core_tools.geometry.set_shared_string_attrib()."""
    mock_set_all = mocker.patch("houdini_core_tools.geometry._set_all_shared_values")
    mock_set_group = mocker.patch("houdini_core_tools.geometry._set_group_shared_values")

    attrib = houdini_core_tools.geometry.find_attrib(obj_test_geo_copy, hou.attribType.Point, attrib_name)
    group = (
        houdini_core_tools.geometry.find_group(obj_test_geo_copy, hou.PointGroup, group_name) if group_name else None
    )

    with context:
        houdini_core_tools.geometry.set_shared_string_attrib(
            attrib,
            "value",
            group=group,
        )

        if group is None:
            mock_set_all.assert_called_with(attrib, "value")

        else:
            mock_set_group.assert_called_with(attrib, group, "value")


def test_shared_edges(obj_test_geo):
    """Test houdini_core_tools.geometry.shared_edges()."""
    pr0, pr1 = obj_test_geo.prims()

    edges = houdini_core_tools.geometry.shared_edges(pr0, pr1)

    pt2 = obj_test_geo.iterPoints()[2]
    pt3 = obj_test_geo.iterPoints()[3]

    edge = obj_test_geo.findEdge(pt2, pt3)

    assert edges == (edge,)
