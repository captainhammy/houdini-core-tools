"""Functions related to Houdini geometry."""

# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Houdini Core Tools
from houdini_core_tools import exceptions

# Houdini
import hou

if TYPE_CHECKING:
    from collections.abc import Sequence


def check_minimum_polygon_vertex_count(
    geometry: hou.Geometry, minimum_vertices: int, *, ignore_open: bool = True
) -> bool:
    """Check that all polygons have a minimum number of vertices.

    This will ignore non-polygon types such as packed and volume primitives.

    Args:
        geometry: The geometry to check.
        minimum_vertices: The minimum number of vertices a polygon must have.
        ignore_open: Ignore polygons which are open.

    Returns:
        Whether all the polygons have the minimum number of vertices.
    """
    for prim in geometry.iterPrimsOfType(hou.primType.Polygon):
        if prim.numVertices() < minimum_vertices:
            if ignore_open and not prim.isClosed():
                continue

            return False

    return True


def connected_points(point: hou.Point) -> tuple[hou.Point, ...]:
    """Get all points that share an edge with the point.

    Args:
        point: The source point.

    Returns:
        Connected points
    """
    prims = point.prims()

    connected = set()

    for prim in prims:
        prim_points = prim.points()

        for prim_point in prim_points:
            if face_has_edge(prim, prim_point, point):
                connected.add(prim_point)

    return tuple(sorted(connected, key=lambda pt: pt.number()))


def face_has_edge(face: hou.Face, point1: hou.Point, point2: hou.Point) -> bool:
    """Test if the face has an edge between two points.

    Args:
        face: The face to check for an edge.
        point1: A point to test for an edge with.
        point2: A point to test for an edge with.

    Returns:
        Whether the points share an edge.
    """
    # Test for the edge.
    edges: tuple[hou.Edge] = face.edges()

    pt_nums = tuple(sorted([point1.number(), point2.number()]))

    for edge in edges:
        edge_pt_nums = tuple(sorted(point.number() for point in edge.points()))

        if edge_pt_nums == pt_nums:
            return True

    return False


def find_attrib(geometry: hou.Geometry, attrib_type: hou.attribType, name: str) -> hou.Attrib | None:
    """Find an attribute with a given name and type on the geometry.

    Args:
        geometry: The geometry to find an attribute on.
        attrib_type: The attribute type.
        name: The attribute name.

    Returns:
        A found attribute, otherwise None.

    Raises:
        UnexpectedAttributeTypeError: When an invalid attrib_type is passed.
    """
    if attrib_type == hou.attribType.Vertex:
        return geometry.findVertexAttrib(name)

    if attrib_type == hou.attribType.Point:
        return geometry.findPointAttrib(name)

    if attrib_type == hou.attribType.Prim:
        return geometry.findPrimAttrib(name)

    if attrib_type == hou.attribType.Global:
        return geometry.findGlobalAttrib(name)

    raise exceptions.UnexpectedAttributeTypeError(attrib_type)


def geo_details_match(geometry1: hou.Geometry, geometry2: hou.Geometry) -> bool:
    """Test if two hou.Geometry objects point to the same detail.

    Args:
        geometry1: A geometry detail.
        geometry2: A geometry detail.

    Returns:
        Whether the objects represent the same detail.
    """
    # pylint: disable=protected-access
    handle1 = geometry1._guDetailHandle()
    handle2 = geometry2._guDetailHandle()

    details_match = int(handle1._asVoidPointer()) == int(handle2._asVoidPointer())

    handle1.destroy()
    handle2.destroy()

    return details_match


def get_points_from_list(geometry: hou.Geometry, point_list: Sequence[int]) -> tuple[hou.Point, ...]:
    """Convert a list of point numbers to hou.Point objects.

    Args:
        geometry: The geometry to get points for.
        point_list: A list of point numbers.

    Returns:
        Matching points on the geometry.
    """
    # Return an empty tuple if the point list is empty.
    if not point_list:
        return ()

    # Convert the list of integers to a space separated string.
    point_str = " ".join([str(i) for i in point_list])

    # Glob for the specified points.
    return geometry.globPoints(point_str)


def get_prims_from_list(geometry: hou.Geometry, prim_list: Sequence[int]) -> tuple[hou.Prim, ...]:
    """Convert a list of primitive numbers to hou.Prim objects.

    Args:
        geometry: The geometry to get prims for.
        prim_list: A list of prim numbers.

    Returns:
        Matching prims on the geometry.
    """
    # Return an empty tuple if the prim list is empty.
    if not prim_list:
        return ()

    # Convert the list of integers to a space separated string.
    prim_str = " ".join([str(i) for i in prim_list])

    # Glob for the specified prims.
    return geometry.globPrims(prim_str)


def geometry_has_prims_with_shared_vertex_points(geometry: hou.Geometry) -> bool:
    """Check if the geometry contains any primitives which have more than one vertex referencing the same point.

    Args:
        geometry: The geometry to check.

    Returns:
        Whether the geometry has any primitives with shared vertex points.
    """
    for prim in geometry.iterPrims():
        vtx_count = prim.numVertices()

        vtx_points = {vertex.point().number() for vertex in prim.vertices()}

        if len(vtx_points) != vtx_count:
            return True

    return False


def get_primitives_with_shared_vertex_points(
    geometry: hou.Geometry,
) -> tuple[hou.Prim, ...]:
    """Get any primitives in the geometry which have more than one vertex referencing the same point.

    Args:
        geometry: The geometry to check.

    Returns:
        A list of any primitives which have shared vertex points.
    """
    prims = []
    for prim in geometry.iterPrims():
        vtx_count = prim.numVertices()

        vtx_points = {vertex.point().number() for vertex in prim.vertices()}

        if len(vtx_points) != vtx_count:
            prims.append(prim)

    return tuple(prims)


def num_points(geometry: hou.Geometry) -> int:
    """Get the number of points in the geometry.

    This should be quicker than len(hou.Geometry.iterPoints()) since it uses
    the 'pointcount' intrinsic value from the detail.

    Args:
        geometry: The geometry to get the point count for.

    Returns:
        The point count:
    """
    return geometry.intrinsicValue("pointcount")


def num_prims(geometry: hou.Geometry) -> int:
    """Get the number of primitives in the geometry.

    This should be quicker than len(hou.Geometry.iterPrims()) since it uses
    the 'primitivecount' intrinsic value from the detail.

    Args:
        geometry: The geometry to get the primitive count for.

    Returns:
        The primitive count:
    """
    return geometry.intrinsicValue("primitivecount")


def num_vertices(geometry: hou.Geometry) -> int:
    """Get the number of vertices in the geometry.

    Args:
        geometry: The geometry to get the vertex count for.

    Returns:
        The vertex count.
    """
    return geometry.intrinsicValue("vertexcount")


def primitive_area(prim: hou.Prim) -> float:
    """Get the area of the primitive.

    This method just wraps the "measuredarea" intrinsic value.

    Args:
        prim: The primitive to get the area of.

    Returns:
        The primitive area.
    """
    return prim.intrinsicValue("measuredarea")


def primitive_bary_center(prim: hou.Prim) -> hou.Vector3:
    """Get the barycenter of the primitive.

    Args:
        prim: The primitive to get the center of.

    Returns:
        The barycenter.
    """
    center = hou.Vector3()

    for vertex in prim.vertices():
        center += vertex.point().position()

    # Construct a vector and return it.
    return center / prim.numVertices()


def primitive_bounding_box(prim: hou.Prim) -> hou.BoundingBox:
    """Get the bounding box of the primitive.

    This method just wraps the "bounds" intrinsic value.

    Args:
        prim: The primitive to get the bounding box of.

    Returns:
        The primitive bounding box.
    """
    bounds = prim.intrinsicValue("bounds")

    # Intrinsic values are out of order for hou.BoundingBox so they need to
    # be shuffled.
    return hou.BoundingBox(bounds[0], bounds[2], bounds[4], bounds[1], bounds[3], bounds[5])


def primitive_perimeter(prim: hou.Prim) -> float:
    """Get the perimeter of the primitive.

    This method just wraps the "measuredperimeter" intrinsic value.

    Args:
        prim: The primitive to get the perimeter of.

    Returns:
        The primitive perimeter.
    """
    return prim.intrinsicValue("measuredperimeter")


def primitive_volume(prim: hou.Prim) -> float:
    """Get the volume of the primitive.

    This method just wraps the "measuredvolume" intrinsic value.

    Args:
        prim: The primitive to get the volume of.

    Returns:
        The primitive volume.
    """
    return prim.intrinsicValue("measuredvolume")


def reverse_prim(prim: hou.Prim) -> None:
    """Reverse the vertex order of the primitive.

    Args:
        prim: The primitive to reverse.

    Raises:
        GeometryPermissionError: If the target geometry is read only.
    """
    geometry = prim.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError

    verb = hou.sopNodeTypeCategory().nodeVerb("reverse")

    new_geo = hou.Geometry()
    verb.execute(new_geo, [geometry])

    geometry.clear()
    geometry.merge(new_geo)


def shared_edges(face1: hou.Face, face2: hou.Face) -> tuple[hou.Edge, ...]:
    """Get a tuple of any shared edges between two primitives.

    Args:
        face1: The face to check for shared edges.
        face2: The other face to check for shared edges.

    Returns:
        A tuple of shared edges.
    """
    geometry = face1.geometry()

    # A list of unique edges.
    edges = set()

    # Iterate over each vertex of the primitive.
    for vertex in face1.vertices():
        # Get the point for the vertex.
        vertex_point = vertex.point()

        # Iterate over all the connected points.
        for connected in connected_points(vertex_point):
            # Sort the points.
            pt1, pt2 = sorted((vertex_point, connected), key=lambda pt: pt.number())

            # Ensure the edge exists for both primitives.
            if face_has_edge(face1, pt1, pt2) and face_has_edge(face2, pt1, pt2):
                # Find the edge and add it to the list.
                edges.add(geometry.findEdge(pt1, pt2))

    return tuple(edges)
