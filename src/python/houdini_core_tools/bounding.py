"""Function related to bounding items."""

# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import hou

# Functions


def bounding_box_area(bbox: hou.BoundingBox) -> float:
    """Calculate the area of this bounding box.

    Args:
        bbox: The bounding box to get the area of.

    Returns:
        The area of the box.
    """
    length, width, height = bbox.sizevec()
    return 2 * (length * width + width * height + height * length)


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
