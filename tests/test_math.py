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


def test_vector_component_along():
    """Test houdini_core_tools.math.vector_component_along()."""
    vec = hou.Vector3(1, 2, 3)

    assert houdini_core_tools.math.vector_component_along(vec, hou.Vector3(0, 0, 15)) == 3.0


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
    "vec,context,expected",
    (
        (hou.Vector3(), pytest.raises(exceptions.VectorIsZeroVectorError), None),  # Test zero-length vector
        (hou.Vector3(2.87, 3.1, -0.5), nullcontext(), hou.Vector3(-0.948531, -1.02455, 0.165249)),
    ),
)
def test_vector_project_along(vec, context, expected):
    """Test houdini_core_tools.math.vector_project_along()."""
    v1 = hou.Vector3(-1.3, 0.5, 7.6)

    with context:
        result = houdini_core_tools.math.vector_project_along(v1, vec)
        assert result.isAlmostEqual(expected)
