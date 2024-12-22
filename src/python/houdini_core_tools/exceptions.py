"""Custom exceptions for houdini_core_tools."""

# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

    import hou


class AttributeNotAStringError(ValueError):
    """Exception for when an attribute is not a string."""

    def __init__(self, attribute: hou.Attrib) -> None:
        super().__init__(f"Attribute '{attribute.name()}' must be a string, got {attribute.dataType()}.")


class InvalidAttributeTypeError(ValueError):
    """Exception for when an attribute is not the expected type."""

    def __init__(self, attribute_type: hou.attribType, expected: Sequence[hou.attribType]) -> None:
        super().__init__(f"Got attribute of type {attribute_type}, expected {', '.join(str(t) for t in expected)}")


class InvalidGroupTypeError(ValueError):
    """Exception for when a group is not the expected type."""

    def __init__(
        self,
        group_type: type[hou.PointGroup | hou.PrimGroup | hou.VertexGroup],
        expected_type: type[hou.PointGroup | hou.PrimGroup | hou.VertexGroup],
    ) -> None:
        super().__init__(f"Got a group of type {group_type}, expected {expected_type}")


class InvalidMultiParmIndicesError(ValueError):
    """Exception for when multiparm indices do not map to an existing parameter."""

    def __init__(self, parameter_name: str) -> None:
        super().__init__(f"Invalid indices: '{parameter_name}' does not exist.")


class MissingMultiParmTokenError(ValueError):
    """Exception for when a parameter name does not contain at least one multiparm token."""

    def __init__(self, parameter_name: str) -> None:
        super().__init__(f"Parameter name '{parameter_name}' must contain at least one #.")


class NotEnoughMultiParmIndicesError(ValueError):
    """Exception for when not enough indices are provided while evaluating multiparm tokens."""

    def __init__(self, name: str, token_count: int, num_indices: int) -> None:
        super().__init__(
            f"Not enough indices provided. Parameter '{name}' expects {token_count}, {num_indices} token(s) provided."
        )


class NoMatchingParameterTemplate(ValueError):
    """Exception for when a node does not have a parameter template of the name."""

    def __init__(self, name: str, node: hou.OpNode) -> None:
        super().__init__(f"Name '{name}' does not map to a parameter on {node.path()}")


class ParameterIsNotAMultiParmInstanceError(ValueError):
    """Exception for when a parameter is not a multiparm instance."""

    def __init__(self, parameter_name: str) -> None:
        super().__init__(f"Parameter '{parameter_name}' is not a multiparm instance.")


class ParameterIsNotAStringError(ValueError):
    """Exception for when a parameter is not a multiparm instance."""

    def __init__(self, parameter_template: hou.ParmTemplate) -> None:
        super().__init__(
            f"Parameter '{parameter_template.name()}' must be a string, got {parameter_template.dataType()}"
        )


class ParameterNotAButtonStripError(ValueError):
    """Exception for when a parameter is not a button strip."""

    def __init__(self, parameter: hou.Parm) -> None:
        super().__init__(f"Parameter '{parameter}' must be a button strip.")


class ParameterTemplateIsNotAMultiParmError(ValueError):
    """Exception for when a parameter template is not a multiparm folder."""

    def __init__(self) -> None:
        super().__init__("Parameter template is not a multiparm folder.")


class ParmTupleTypeError(ValueError):
    """Exception raised when a parameter tuple is not of a certain special type."""

    def __init__(self, parm_tuple: hou.ParmTuple, expected_type: str) -> None:
        super().__init__(f"Parm tuple '{parm_tuple}' is not a {expected_type}.")


class PrimitiveIsRawGeometryError(ValueError):
    """Exception for when a point is bound to a primitive that is raw geometry."""

    def __init__(self, point: hou.Point) -> None:
        super().__init__(f"Point {point.number()} is bound to raw geometry.")


class UnexpectedAttributeTypeError(ValueError):
    """Exception for passing an invalid hou.attribType value."""

    def __init__(self, value: Any) -> None:
        super().__init__(f"Expected a hou.attribType value, got {type(value)}")


class UnexpectedGroupTypeError(ValueError):
    """Exception for passing an invalid group type value."""

    def __init__(self, value: type[Any]) -> None:
        super().__init__(f"Expected a valid geometry group type, got {value}")


class UnsupportedCategoryError(ValueError):
    """Exception raised when an invalid node type category is passed.

    Args:
        category: The invalid node type category.
    """

    def __init__(self, category: hou.NodeTypeCategory) -> None:
        super().__init__(f"Unknown category type {category.name()}")


class VectorIsZeroVectorError(ValueError):
    """Exception for a zero vector being passed."""

    def __init__(self) -> None:
        super().__init__("Vector must be non-zero.")
