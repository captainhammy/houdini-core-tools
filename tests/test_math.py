"""Test the houdini_core_tools.math module."""

# Standard Library
from contextlib import nullcontext

# Third Party
import pytest

# Houdini Core Tools
import houdini_core_tools.math
from houdini_core_tools import exceptions

# Houdini
import hou

# Tests


@pytest.mark.parametrize(
    "args,kwargs,expected",
    (
        (
            (hou.Vector3(-1, 2, 4), hou.Vector3(1, 1, 1)),
            {"pscale": 1.5, "up_vector": hou.Vector3(1, 1, -1)},
            hou.Matrix4((
                (1.0606601717798214, -1.0606601717798214, 0.0, 0.0),
                (0.61237243569579436, 0.61237243569579436, -1.2247448713915889, 0.0),
                (0.86602540378443882, 0.86602540378443882, 0.86602540378443882, 0.0),
                (-1.0, 2.0, 4.0, 1.0),
            )),
        ),
        (  # Test up vector is zero-vector
            (hou.Vector3(-1, 2, 4), hou.Vector3(1, 1, 1)),
            {"pscale": 1.5, "up_vector": hou.Vector3()},
            hou.Matrix4((
                (0.4999999701976776, -1.0000000298023224, -1.0000000298023224, 0.0),
                (-1.0000000298023224, 0.4999999701976776, -1.0000000298023224, 0.0),
                (-1.0000000298023224, -1.0000000298023224, 0.4999999701976776, 0.0),
                (-1.0, 2.0, 4.0, 1.0),
            )),
        ),
        (  # By orient
            (hou.Vector3(-1, 2, 4),),
            {"orient": hou.Quaternion(0.3, -1.7, -0.9, -2.7)},
            hou.Matrix4((
                (0.33212996389891691, 0.3465703971119134, -0.87725631768953083, 0.0),
                (-0.53068592057761732, 0.83754512635379064, 0.1299638989169675, 0.0),
                (0.77978339350180514, 0.42238267148014441, 0.46209386281588438, 0.0),
                (-1.0, 2.0, 4.0, 1.0),
            )),
        ),
        (  # Test with additional translation.
            (hou.Vector3(-1, 2, 4), hou.Vector3(1, 1, 1)),
            {
                "pscale": 1.5,
                "up_vector": hou.Vector3(1, 1, -1),
                "trans": hou.Vector3(0, -3, 2),
            },
            hou.Matrix4((
                (1.0606601717798214, -1.0606601717798214, 0.0, 0.0),
                (0.6123724356957944, 0.6123724356957944, -1.224744871391589, 0.0),
                (0.8660254037844388, 0.8660254037844388, 0.8660254037844388, 0.0),
                (-1.0, -1.0, 6.0, 1.0),
            )),
        ),
        (  # Test with additional rotation.
            (
                hou.Vector3(-1, 2, 4),
                hou.Vector3(1, 1, 1),
            ),
            {
                "pscale": 1.5,
                "up_vector": hou.Vector3(1, 1, -1),
                "rot": hou.Quaternion((-0.49999999144286444, 0.49999999144286444, 0.0, 0.7071067811865476)),
            },
            hou.Matrix4((
                (1.0606601717798214, -1.0606601717798214, 0.0, 0.0),
                (-0.8660253933041303, -0.8660253933041303, -0.8660254247450543, 0.0),
                (0.6123724505171884, 0.6123724505171884, -1.224744856570195, 0.0),
                (-1.0, 2.0, 4.0, 1.0),
            )),
        ),
        (  # Test with additional scale input.
            (
                hou.Vector3(-1, 2, 4),
                hou.Vector3(1, 1, 1),
            ),
            {
                "up_vector": hou.Vector3(1, 1, -1),
                "scale": hou.Vector3(1, 1.4, 2),
            },
            hou.Matrix4((
                (0.7071067811865476, -0.7071067811865476, 0.0, 0.0),
                (0.5715476066494081, 0.5715476066494081, -1.1430952132988164, 0.0),
                (1.1547005383792517, 1.1547005383792517, 1.1547005383792517, 0.0),
                (-1.0, 2.0, 4.0, 1.0),
            )),
        ),
        (  # Test with pivot point
            (
                hou.Vector3(-1, 2, 4),
                hou.Vector3(1, 1, 1),
            ),
            {
                "up_vector": hou.Vector3(1, 1, -1),
                "pivot": hou.Vector3(10, -4, 45),
            },
            hou.Matrix4((
                (0.7071067811865476, -0.7071067811865476, 0.0, 0.0),
                (0.4082482904638629, 0.4082482904638629, -0.816496580927726, 0.0),
                (0.5773502691896258, 0.5773502691896258, 0.5773502691896258, 0.0),
                (-32.41883676354318, -15.276701139812236, -25.24674843724407, 1.0),
            )),
        ),
    ),
)
def test_build_instance_matrix(args, kwargs, expected):
    """Test houdini_core_tools.math.build_instance_matrix()."""
    mat = houdini_core_tools.math.build_instance_matrix(*args, **kwargs)

    assert mat.isAlmostEqual(expected)


@pytest.mark.parametrize(
    "mat,expected",
    (
        (hou.Matrix3(), False),
        (hou.Matrix3(1), True),  # Single value sets the diagonal, thus it is the identity matrix.
        (hou.Matrix4(), False),
        (hou.hmath.identityTransform(), True),
    ),
)
def test_matrix_is_identity(mat, expected):
    """Test houdini_core_tools.math.matrix_is_identity()."""
    assert houdini_core_tools.math.matrix_is_identity(mat) == expected


@pytest.mark.parametrize(
    "translates",
    (
        hou.Vector3(1, 2, 3),
        (4, 5, 6),
    ),
)
def test_matrix_set_translates(translates):
    """Test houdini_core_tools.math.matrix_set_translates()."""
    identity = hou.hmath.identityTransform()
    houdini_core_tools.math.matrix_set_translates(identity, translates)

    if not isinstance(translates, hou.Vector3):
        translates = hou.Vector3(*translates)

    assert identity.extractTranslates() == translates


@pytest.mark.parametrize("vec,direction,expected", ((hou.Vector3(1, 2, 3), hou.Vector3(0, 0, 15), 3.0),))
def test_vector_component_along(vec, direction, expected):
    """Test houdini_core_tools.math.vector_component_along()."""
    assert houdini_core_tools.math.vector_component_along(vec, direction) == expected


@pytest.mark.parametrize(
    "vec,expected,test_vec",
    (
        (
            hou.Vector3(1, 2, 3),
            hou.Matrix3(((0, -3, 2), (3, 0, -1), (-2, 1, 0))),
            hou.Vector3(6.82, -0.48, 2.86),
        ),
    ),
)
def test_vector_compute_dual(vec, expected, test_vec):
    """Test houdini_core_tools.math.vector_compute_dual()."""
    result = houdini_core_tools.math.vector_compute_dual(vec)
    assert result == expected

    # Test that the result also satisfies the equivalency of
    # - A = vector_compute_dual(a); c = b * A.transposed()
    # - c = cross(a, b)
    assert vec.cross(test_vec) == test_vec * result.transposed()


@pytest.mark.parametrize(
    "vec,expected",
    (
        ((), False),
        (hou.Vector2(1, 0), False),
        (hou.Vector2(float("nan"), 1), True),
        (hou.Vector3(6.5, 1, float("nan")), True),
        (hou.Vector4(-4.0, 5, -0, float("nan")), True),
    ),
)
def test_vector_contains_nans(vec, expected):
    """Test houdini_core_tools.math.vector_contains_nans()."""
    result = houdini_core_tools.math.vector_contains_nans(vec)
    assert result == expected


@pytest.mark.parametrize(
    "v1, v2,context,expected",
    (
        (
            hou.Vector3(-1.3, 0.5, 7.6),
            hou.Vector3(),
            pytest.raises(exceptions.VectorIsZeroVectorError),
            None,
        ),  # Test zero-length vector
        (
            hou.Vector3(-1.3, 0.5, 7.6),
            hou.Vector3(2.87, 3.1, -0.5),
            nullcontext(),
            hou.Vector3(-0.948531, -1.02455, 0.165249),
        ),
    ),
)
def test_vector_project_along(v1, v2, context, expected):
    """Test houdini_core_tools.math.vector_project_along()."""
    with context:
        result = houdini_core_tools.math.vector_project_along(v1, v2)
        assert result.isAlmostEqual(expected)
