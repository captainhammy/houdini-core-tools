"""Test the houdini_core_tools.menus module."""

# Third Party
import pytest

# Houdini Core Tools
from houdini_core_tools import menus

# Tests


def test_format_label_for_icon():
    """Test houdini_core_tools.menus.format_label_for_icon()."""
    result = menus.format_label_for_icon("label_value", "SOP_box")

    assert result == "![SOP_box]label_value"


def test_format_orange_label_text():
    """Test houdini_core_tools.menus.format_orange_label_text()."""
    result = menus.format_orange_label_text("label_value")

    assert result == "\x02label_value"


def test_get_menu_separator_entry():
    """Test houdini_core_tools.menus.get_menu_separator_entry()."""
    result = menus.get_menu_separator_entry()

    assert result == (menus.SEPARATOR_TOKEN, menus.SEPARATOR_VALUE)


@pytest.mark.parametrize(
    ("pre_items", "add_sep", "expected"),
    [
        (
            None,
            True,
            (0, 0, 1, 1),
        ),  # Verify separator is only added with pre-items.
        ([("token", "label")], False, ("token", "label", 0, 0, 1, 1)),
        (
            [("token", "label")],
            True,
            (
                "token",
                "label",
                menus.SEPARATOR_TOKEN,
                menus.SEPARATOR_VALUE,
                0,
                0,
                1,
                1,
            ),
        ),
    ],
)
def test_make_houdini_menu(pre_items, add_sep, expected):
    """Test houdini_core_tools.menus.make_houdini_menu()."""

    @menus.make_houdini_menu(pre_items=pre_items, add_separator=add_sep)
    def make_menu_test():
        return list(range(2))

    result = make_menu_test()

    assert result == expected
