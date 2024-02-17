"""This module contains functions supporting custom OPmenu.xml entries."""

# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import hou

# Functions


def create_absolute_reference_copy(scriptargs: dict) -> hou.Node:
    """Create an absolute reference copy of a node.

    Args:
        scriptargs: kwargs dict from OPmenu entry.

    Returns:
        The created reference copy node.
    """
    node = scriptargs["node"]

    result = node.parent().copyItems([node], channel_reference_originals=True, relative_references=False)

    return result[0]


def unlock_parents(scriptargs: dict) -> None:
    """Unlock all parent digital assets.

    Args:
        scriptargs: kwargs dict from OPmenu entry.
    """
    node = scriptargs["node"]
    node.parent().allowEditingOfContents(propagate=True)


def unlock_parents_context(scriptargs: dict) -> bool:
    """Check if we should show the 'Unlock All Parent Digital Assets' entry.

    Args:
        scriptargs: kwargs dict from OPmenu entry.

    Returns:
        Whether to show the OPmenu entry.
    """
    node = scriptargs["node"]
    return node.isInsideLockedHDA()
