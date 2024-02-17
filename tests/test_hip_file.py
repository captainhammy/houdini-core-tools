"""Test the houdini_core_tools.hip_file module."""

# Standard Library
import os

# Third Party
import pytest

# Houdini Core Tools
from houdini_core_tools import hip_file

# Houdini
import hou

# Fixtures


@pytest.fixture
def restore_frange_settings():
    """Restore the current frame and range settings after testing."""
    current_frame = hou.frame()
    frame_range = hou.playbar.frameRange()
    playback_range = hou.playbar.playbackRange()

    yield

    hou.playbar.setFrameRange(*frame_range)
    hou.playbar.setPlaybackRange(*playback_range)
    hou.setFrame(current_frame)


# Tests


@pytest.mark.usefixtures("restore_frange_settings")
@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("untitled.hip", None),  # No match
        ("hipname_v00.hip", "00"),  # Single match
        ("hipname_v01.hip", "01"),  # Single match
        ("hipname.v01.hip", "01"),  # .v# instead of _v#
        ("hipname_v00003.hip", "03"),  # excess padding
        ("hipname_v02.03.hip", "02"),  # Ignore minor versioning
        ("hipname_v05_alternate_v01.hip", "01"),  # Multiple 'versions'
        ("hipname_v3021.hip", "3021"),  # Really large version number
    ],
)
def test_hip_version(name, expected):
    """Test houdini_core_tools.hip_file.hip_version()."""
    hou.hipFile.setName(name)

    result = hip_file.hip_version()

    assert result == expected


@pytest.mark.parametrize("as_str", [False, True])
def test_save_copy(tmp_path, as_str):
    """Test houdini_core_tools.hip_file.save_copy()."""
    current_name = hou.hipFile.name()

    target_path = tmp_path / f"test_copy_{as_str}.hip"

    if as_str:
        target_path = target_path.as_posix()

    hip_file.save_copy(target_path)

    assert os.path.exists(target_path)  # noqa: PTH110

    # Try to verify that the file wasn't added to the recent files list.
    try:
        history = hou.findFile("file.history")

    except hou.OperationFailed:
        pass

    else:
        contents = hou.readFile(history)

        assert f"test_copy_{as_str}.hip" not in contents

    assert hou.hipFile.name() == current_name


@pytest.mark.usefixtures("restore_frange_settings")
@pytest.mark.parametrize(
    ("start", "end", "current", "expected"),
    [
        (1001, 1010, 1003, None),  # Current frame is within the new range
        (1001, 1010, 1001, None),  # Current frame is start of new range
        (1001.0, 1010.0, 1010.0, None),  # Current frame is end of new range
        (1001, 1010, 1011, 1001),  # Current frame > new range
        (1001.0, 1010.0, 1000.0, 1001.0),  # Current frame < new range
    ],
)
def test_set_frame_range(start, end, current, expected):
    """Test houdini_core_tools.hip_file.set_frame_range()."""
    hou.setFrame(current)

    hip_file.set_frame_range(start, end)

    assert hou.playbar.frameRange() == hou.Vector2(start, end)
    assert hou.playbar.playbackRange() == hou.Vector2(start, end)

    if expected is not None:
        assert hou.frame() == expected

    else:
        assert hou.frame() == current
