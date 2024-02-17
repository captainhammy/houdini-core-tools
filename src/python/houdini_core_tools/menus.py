"""Functions and tools to deal with Houdini parameter menus."""

# Future
from __future__ import annotations

# Standard Library
import functools
from typing import Callable, Sequence

# Globals

SEPARATOR_TOKEN = "__separator__"
"""This is the token Houdini will use to define a separator in a menu parameter."""

SEPARATOR_VALUE = ""
"""The value doesn't actually matter for a separator so just use an empty string."""

# Functions


def format_label_for_icon(label: str, icon_name: str) -> str:
    """Format a menu label to include an icon.

    Args:
        label: The menu label value.
        icon_name: The icon to use.

    Returns:
        The formatted label value.
    """
    return f"![{icon_name}]{label}"


def format_orange_label_text(label: str) -> str:
    """Format a menu label to be orange.

    Args:
        label: The menu label value.

    Returns:
        The formatted label value.
    """
    return f"{chr(2)}{label}"


def get_menu_separator_entry() -> tuple[str, str]:
    """Get the required token and value to add a separator to a parameter menu.

    Returns:
        The separator token and value pair.
    """
    return SEPARATOR_TOKEN, SEPARATOR_VALUE


def make_houdini_menu(pre_items: Sequence[tuple[str, str]] | None = None, *, add_separator: bool = False) -> Callable:
    """Function decorator which takes a list of strings and converts it to a Houdini style menu.

    >>> @make_houdini_menu(pre_items=[('z', 'y')], add_separator=True)
    ... def menu_builder():
    ...     return ['a', 'b', 'c']
    ...
    >>> print(menu_builder())
    ['z', 'y', '__separator__', '', 'a', 'a', 'b', 'b', 'c', 'c']

    Args:
        pre_items: Optional items to insert before the generated values.
        add_separator: Whether to add a separator after the pre-item entries.

    Returns:
        The wrapped function.
    """

    def decorator(func):  # type: ignore
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # type: ignore
            # Store the wrapped function result.
            result = func(*args, **kwargs)

            menu = []

            if pre_items is not None:
                for item in pre_items:
                    menu.extend(item)

                if add_separator:
                    menu.extend(get_menu_separator_entry())

            # Add the result values as token/label pairs.
            for value in result:
                menu.extend((value, value))

            return tuple(menu)

        return wrapper

    return decorator
