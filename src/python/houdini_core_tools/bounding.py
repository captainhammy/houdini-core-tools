"""Function related to bounding items."""

# Future
from __future__ import annotations

# Houdini
import hou

# Functions


def add_to_bounding_box_min(bbox: hou.BoundingBox, vec: hou.Vector3) -> None:
    """Add values to the minimum bounds of this bounding box.

    Args:
        bbox: The bounding box to expand.
        vec: The values to add.
    """
    bbox.setTo(tuple(bbox.minvec() + vec) + tuple(bbox.maxvec()))


def add_to_bounding_box_max(bbox: hou.BoundingBox, vec: hou.Vector3) -> None:
    """Add values to the maximum bounds of this bounding box.

    Args:
        bbox: The bounding box to expand.
        vec: The values to add.
    """
    bbox.setTo(tuple(bbox.minvec()) + tuple(bbox.maxvec() + vec))


def bounding_box_area(bbox: hou.BoundingBox) -> float:
    """Calculate the area of this bounding box.

    Args:
        bbox: The bounding box to get the area of.

    Returns:
        The area of the box.
    """
    length, width, height = bbox.sizevec()
    return 2 * (length * width + width * height + height * length)


def bounding_box_is_inside(source_bbox: hou.BoundingBox, target_bbox: hou.BoundingBox) -> bool:
    """Determine if this bounding box is totally enclosed by another box.

    Args:
        source_bbox: The bounding box to check for being enclosed.
        target_bbox: The bounding box to check for enclosure.

    Returns:
        Whether this object is totally enclosed by the other box.
    """
    return (
        source_bbox.maxvec().x() < target_bbox.maxvec().x()
        and source_bbox.maxvec().y() < target_bbox.maxvec().y()
        and source_bbox.maxvec().z() < target_bbox.maxvec().z()
        and source_bbox.minvec().x() > target_bbox.minvec().x()
        and source_bbox.minvec().y() > target_bbox.minvec().y()
        and source_bbox.minvec().z() > target_bbox.minvec().z()
    )


def bounding_box_volume(bbox: hou.BoundingBox) -> float:
    """Calculate the volume of this bounding box.

    Args:
        bbox: The bounding box to get the volume of.

    Returns:
        The volume of the box.
    """
    result = 1

    for comp in bbox.sizevec():
        result *= comp

    return result


def bounding_boxes_intersect(bbox1: hou.BoundingBox, bbox2: hou.BoundingBox) -> bool:
    """Determine if the bounding boxes intersect.

    Args:
        bbox1: A bounding box to check for intersection with.
        bbox2: A bounding box to check for intersection with.

    Returns:
        Whether this object intersects the other box.
    """
    b1_min = bbox1.minvec()
    b1_max = bbox1.maxvec()
    b2_min = bbox2.minvec()
    b2_max = bbox2.maxvec()

    # This implementation is copied from UT_BoundingBox.h

    if b1_min.x() > b2_max.x() or b1_max.x() < b2_min.x():
        return False

    if b1_min.y() > b2_max.y() or b1_max.y() < b2_min.y():
        return False

    return not (b1_min.z() > b2_max.z() or b1_max.z() < b2_min.z())


def compute_bounding_box_intersection(bbox1: hou.BoundingBox, bbox2: hou.BoundingBox) -> hou.BoundingBox | None:
    """Compute the intersection of two bounding boxes.

    Args:
        bbox1: A box to compute intersection with.
        bbox2: A box to compute intersection with.

    Returns:
        The intersection of the bounding boxes, otherwise None if they do not intersect.
    """
    # This implementation is copied from UT_BoundingBox.h
    if not bounding_boxes_intersect(bbox1, bbox2):
        return None

    result_bbox = hou.BoundingBox()

    b1_min = bbox1.minvec()
    b1_max = bbox1.maxvec()
    b2_min = bbox2.minvec()
    b2_max = bbox2.maxvec()

    x_min = max(b1_min.x(), b2_min.x())
    x_max = min(b1_max.x(), b2_max.x())

    y_min = max(b1_min.y(), b2_min.y())
    y_max = min(b1_max.y(), b2_max.y())

    z_min = max(b1_min.z(), b2_min.z())
    z_max = min(b1_max.z(), b2_max.z())

    result_bbox.setTo((x_min, y_min, z_min, x_max, y_max, z_max))
    return result_bbox


def expand_bounding_box(bbox: hou.BoundingBox, delta_x: float, delta_y: float, delta_z: float) -> None:
    """Expand the min and max bounds in each direction by the axis delta.

    Args:
        bbox: The bounding box to expand.
        delta_x: The X value to expand by.
        delta_y: The Y value to expand by.
        delta_z: The Z value to expand by.
    """
    expand_vec = hou.Vector3(delta_x, delta_y, delta_z)
    min_vec = bbox.minvec() - expand_vec
    max_vec = bbox.maxvec() + expand_vec

    bbox.setTo(tuple(min_vec) + tuple(max_vec))
