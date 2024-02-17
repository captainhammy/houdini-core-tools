"""Functions and tools for dealing with the node graph."""

# Future
from __future__ import annotations

# Standard Library
import enum
import functools
from typing import Callable

# Third Party
from singleton import Singleton

# Houdini
import nodegraphtitle

# Enums


class NodeGraphTitleLocation(enum.Enum):
    """Enum for selecting the title location."""

    LEFT = "left"
    RIGHT = "right"


# Classes


class NodeGraphTitleManager(metaclass=Singleton):
    """Manager for setting node graph titles."""

    def __init__(self) -> None:
        # Store references to the original functions.
        self._original_left = nodegraphtitle.networkEditorTitleLeft
        self._original_right = nodegraphtitle.networkEditorTitleRight

    # Non-Public Methods

    def _set_title(
        self,
        location: NodeGraphTitleLocation,
        value_func: Callable,
        *,
        include_default: bool = True,
    ) -> None:
        """Set a dynamic title value for the selected title field.

        Args:
            location: The title location to modify.
            value_func: A callable to provide the title value.
            include_default: Whether to include the default title information.
        """
        original = getattr(self, f"_original_{location.value}")

        def title_wrapper(*args, **kwargs):  # type: ignore
            value = value_func()

            title = original(*args, **kwargs) if include_default else ""

            return f"{value} - {title}" if title else value

        setattr(nodegraphtitle, f"networkEditorTitle{location.value.title()}", title_wrapper)
        functools.update_wrapper(title_wrapper, original)

    # Methods

    def reset_title(self, location: NodeGraphTitleLocation) -> None:
        """Reset the left title to the default.

        Args:
            location: The title location to reset.
        """
        original = getattr(self, f"_original_{location.value}")

        setattr(nodegraphtitle, f"networkEditorTitle{location.value.title()}", original)

    def set_dynamic_title(
        self,
        location: NodeGraphTitleLocation,
        value_func: Callable,
        *,
        include_default: bool = True,
    ) -> None:
        """Set a dynamic title value for the selected title field.

        The value function will be called whenever the node graph is refreshed.

        Args:
            location: The title location to modify.
            value_func: A callable to provide the title value.
            include_default: Whether to include the default title information.
        """
        self._set_title(location, value_func, include_default=include_default)

    def set_static_title(self, location: NodeGraphTitleLocation, value: str, *, include_default: bool = True) -> None:
        """Set a static title value for the left title field.

        Args:
            location: The title location to modify.
            value: The value to set.
            include_default: Whether to include the default title information.
        """

        def value_func():  # type: ignore
            return value

        self.set_dynamic_title(location, value_func, include_default=include_default)
