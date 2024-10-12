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


def num_prim_vertices(prim: hou.Prim) -> int:
    """Get the number of vertices belonging to the primitive.

    Args:
        prim: The primitive to get the vertex count of.

    Returns:
        The vertex count.
    """
    return prim.intrinsicValue("vertexcount")


def primitive_area(prim: hou.Prim) -> float:
    """Get the area of the primitive.

    This method just wraps the "measuredarea" intrinsic value.

    Args:
        prim: The primitive to get the area of.

    Returns:
        The primitive area.
    """
    return prim.intrinsicValue("measuredarea")


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
