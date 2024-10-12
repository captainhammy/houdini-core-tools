"""Custom exceptions for houdini_core_tools."""

# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import hou


class ParameterNotAButtonStripError(ValueError):
    """Exception for when a parameter is not a button strip."""

    def __init__(self, parameter: hou.Parm) -> None:
        super().__init__(f"Parameter {parameter} must be a button strip.")


class ParameterTemplateIsNotAMultiparmError(ValueError):
    """Exception for when a parameter template is not a multiparm folder."""

    def __init__(self) -> None:
        super().__init__("Parameter template is not a multiparm folder.")


class ParmTupleTypeError(ValueError):
    """Exception raised when a parameter tuple is not of a certain special type."""

    def __init__(self, parm_tuple: hou.ParmTuple, expected_type: str) -> None:
        super().__init__(f"Parm tuple {parm_tuple} is not a {expected_type}.")


class UnexpectedAttributeTypeError(ValueError):
    """Exception for passing an invalid hou.attribType value."""

    def __init__(self, value: Any) -> None:
        super().__init__(f"Expected a hou.attribType value, got {type(value)}")


class VectorIsZeroVectorError(ValueError):
    """Exception for a zero vector being passed."""

    def __init__(self) -> None:
        super().__init__("Vector must be non-zero.")
