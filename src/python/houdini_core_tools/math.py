"""Functions related to math in Houdini."""

# Future
from __future__ import annotations

# Standard Library
import math

# Houdini Core Tools
from houdini_core_tools import exceptions

# Houdini
import hou


def build_instance_matrix(  # noqa: PLR0913,PLR0917
    position: hou.Vector3,
    direction: hou.Vector3 | None = None,
    pscale: float = 1.0,
    scale: hou.Vector3 | None = None,
    up_vector: hou.Vector3 | None = None,
    rot: hou.Quaternion | None = None,
    trans: hou.Vector3 | None = None,
    pivot: hou.Vector3 | None = None,
    orient: hou.Quaternion | None = None,
) -> hou.Matrix4:
    """Compute a transform to orient to a given direction.

    The transform can be computed for an optional position and scale.

    The up vector is optional and will orient the matrix to this up vector.  If
    no up vector is given, the Z axis will be oriented to point in the supplied
    direction.

    If a rotation quaternion is specified, the orientation will be additionally
    transformed by the rotation.

    If a translation is specified, the entire frame of reference will be moved
    by this translation (unaffected by the scale or rotation).

    If a pivot is specified, use it as the local transformation of the
    instance.

    If `orient` is specified, the orientation (using the
    direction and up vector) will not be performed and this orientation will
    instead be used to define an original orientation.

    See https://www.sidefx.com/docs/houdini//copy/instanceattrs.html for more details.

    Args:
        position: The position of the object to transform.
        direction: "Velocity" vector. Uses (0, 0, 1) if not defined.
        pscale: Uniform scaling.
        scale: Optional non-uniform scale.  Uses (1, 0, 1) if not defined.
        up_vector: Optional up vector when not using `orient`.  Uses (0, 1, 0) if not defined.
        rot: Optional additional rotation. Uses (0, 0, 0, 1) if not defined.
        trans: Optional additional translation. Uses (0, 0, 0) if not defined.
        pivot: Optional local pivot point. Uses (0, 0, 0) if not defined.
        orient: Optional orientation quaternion to use instead of calculating.

    Returns:
        The computed instance transform matrix.
    """
    if direction is None:
        direction = hou.Vector3(0, 0, 1)

    if scale is None:
        scale = hou.Vector3(1, 1, 1)

    if up_vector is None:
        up_vector = hou.Vector3(0, 1, 0)

    if rot is None:
        rot = hou.Quaternion(0, 0, 0, 1)

    if trans is None:
        trans = hou.Vector3(0, 0, 0)

    if pivot is None:
        pivot = hou.Vector3(0, 0, 0)

    zero_vec = hou.Vector3()

    # Scale the non-uniform scale by the uniform scale.
    scale *= pscale

    # Construct the scale matrix.
    scale_matrix = hou.hmath.buildScale(scale)

    # Build a rotation matrix from the rotation quaternion.
    rot_matrix = hou.Matrix4(rot.extractRotationMatrix3())

    # Translate by -pivot
    pivot_matrix = hou.hmath.buildTranslate(-pivot)

    # Build a translation matrix from the position and the translation vector.
    trans_matrix = hou.hmath.buildTranslate(position + trans)

    # If an orientation quaternion is passed, construct a matrix from it.
    if orient is not None:
        alignment_matrix = hou.Matrix4(orient.extractRotationMatrix3())

    # If the up vector is not the zero vector, build a lookat matrix
    # between the direction and zero vectors using the up vector.
    elif up_vector != zero_vec:
        alignment_matrix = hou.Matrix4(
            hou.hmath.buildRotateLookAt(direction, zero_vec, up_vector).extractRotationMatrix3()
        )

    # If the up vector is the zero vector, build a matrix from the
    # dihedral.
    else:
        alignment_matrix = zero_vec.matrixToRotateTo(direction)

    # Return the instance transform matrix.
    return pivot_matrix * scale_matrix * alignment_matrix * rot_matrix * trans_matrix


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


def vector_compute_dual(vector: hou.Vector3) -> hou.Matrix3:
    """Compute the dual of the vector.

    The dual is a matrix which acts like the cross product when multiplied by
    other vectors.

    The following are equivalent:
        - A = vector_compute_dual(a) ; c = b * A.transposed()
        - c = cross(a, b)

    Args:
        vector: The vector to compute the dual for

    Returns:
        The dual of the vector.
    """
    return hou.Matrix3((
        (0, -vector.z(), vector.y()),
        (vector.z(), 0, -vector.x()),
        (-vector.y(), vector.x(), 0),
    ))


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
