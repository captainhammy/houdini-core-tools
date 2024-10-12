"""Functions related to math in Houdini."""

# Future
from __future__ import annotations

# Standard Library
import math

# Houdini Core Tools
from houdini_core_tools import exceptions

# Houdini
import hou


def matrix_is_identity(matrix: hou.Matrix3 | hou.Matrix4) -> bool:
    """Check if the matrix is the identity matrix.

    Args:
        matrix: The matrix to check.

    Returns:
        Whether the matrix is the identity matrix.
    """
    # We are a 3x3 matrix.
    if isinstance(matrix, hou.Matrix3):
        # Construct a new 3x3 matrix.
        mat = hou.Matrix3()

        # Set it to be the identity.
        mat.setToIdentity()

        # Compare the two.
        return matrix == mat

    # Compare against the identity transform from hmath.
    return matrix == hou.hmath.identityTransform()


def matrix_set_translates(matrix: hou.Matrix4, translates: tuple[float, float, float] | hou.Vector3) -> None:
    """Set the translation values of this matrix.

    Args:
        matrix: The matrix to set the translations for.
        translates: The translation values to set.
    """
    # The translations are stored in the first 3 columns of the last row of the
    # matrix.  To set the values we just need to set the corresponding columns
    # to the matching components in the vector.
    for i in range(3):
        matrix.setAt(3, i, translates[i])


def vector_component_along(vector: hou.Vector3, target_vector: hou.Vector3) -> float:
    """Calculate the component of this vector along the target vector.

    Args:
        vector: The vector whose component along we want to get.
        target_vector: The vector to calculate against.

    Returns:
        The component of this vector along the other vector.
    """
    # The component of vector A along B is: A dot (unit vector // to B).
    return vector.dot(target_vector.normalized())


def vector_contains_nans(vector: hou.Vector2 | hou.Vector3 | hou.Vector4) -> bool:
    """Check if the vector contains NaNs.

    Args:
        vector: The vector to check for NaNs.

    Returns:
        Whether there are any NaNs in the vector.
    """
    return any(math.isnan(component) for component in vector)


def vector_project_along(vector: hou.Vector3, target_vector: hou.Vector3) -> hou.Vector3:
    """Calculate the vector projection of this vector onto another vector.

    This is an orthogonal projection of this vector onto a straight line
    parallel to the supplied vector.

    Args:
        vector: The vector to project.
        target_vector: The vector to project onto.

    Returns:
        The vector projected along the other vector.

    Raises:
        ValueError: If the target vector is the zero vector.
    """
    # The vector cannot be the zero vector.
    if target_vector == hou.Vector3():
        raise exceptions.VectorIsZeroVectorError

    return target_vector.normalized() * vector_component_along(vector, target_vector)
