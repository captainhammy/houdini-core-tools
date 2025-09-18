"""Test the houdini_core_tools.hip_file module."""

# Standard Library
import contextlib
import datetime
import os
from contextlib import nullcontext

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


@pytest.mark.parametrize(
    "variable,expected",
    (
        ("_HIP_SAVETIME", "Wed Feb  5 05:33:57 2025"),
        ("_HIP_FOO", None),
    ),
)
def test__get_global_variable_value_from_file(shared_datadir, variable, expected):
    """Test houdini_core_tools.hip_file._get_global_variable_value_from_file()."""
    result = hip_file._get_global_variable_value_from_file(shared_datadir / "test_hip_saved_data.hiplc", variable)

    assert result == expected


@pytest.mark.parametrize(
    "has_unsaved,prompt,ui_available,choice,context",
    (
        (False, False, False, 0, contextlib.nullcontext()),  # No unsaved
        (True, False, False, 0, pytest.raises(hou.OperationFailed, match="unsaved changes")),  # Unsaved, no prompt
        (True, True, False, 0, pytest.raises(hou.OperationFailed, match="unsaved changes")),  # Unsaved, prompt, no ui
        (True, True, True, 0, nullcontext()),  # Unsaved, prompt and save
        (True, True, True, 1, pytest.raises(hou.OperationFailed, match="declined")),  # Unsaved, prompt and no save
    ),
)
def test_check_unsaved_changes(mocker, mock_hou_ui, has_unsaved, prompt, choice, ui_available, context):
    """Test houdini_core_tools.hip_file.check_unsaved_changes()."""
    mocker.patch("hou.isUIAvailable", return_value=ui_available)
    mocker.patch("hou.hipFile.hasUnsavedChanges", return_value=has_unsaved)
    mock_save = mocker.patch("hou.hipFile.save")

    mock_hou_ui.displayCustomConfirmation.return_value = choice

    sentinel = mocker.MagicMock()

    @hip_file.check_unsaved_changes(prompt=prompt)
    def test():
        sentinel()

    with context:
        test()
        sentinel.assert_called()

    if has_unsaved and prompt and ui_available:
        mock_hou_ui.displayCustomConfirmation.asssert_called()

        assert mock_save.call_count == (1 if choice == 0 else 0)


@pytest.mark.parametrize(
    "hip_name,expected",
    (
        ("test_hip_saved_data.hiplc", datetime.datetime(2025, 2, 5, 5, 33, 57)),
        (None, None),
    ),
)
def test_get_hip_save_time_from_file(mocker, shared_datadir, hip_name, expected):
    """Test houdini_core_tools.hip_file.get_hip_save_time_from_file()."""
    mock_value = "Wed Feb  5 05:33:57 2025" if hip_name is not None else None
    mocker.patch("houdini_core_tools.hip_file._get_global_variable_value_from_file", return_value=mock_value)

    hip_path = shared_datadir / "test_hip_saved_data.hiplc"

    result = hip_file.get_hip_save_time_from_file(hip_path)

    assert result == expected

    result = hip_file.get_hip_save_time_from_file(hip_path.as_posix())

    assert result == expected


@pytest.mark.parametrize(
    "hip_name,expected",
    (
        ("test_hip_saved_data.hiplc", (20, 5, 493)),
        (None, None),
    ),
)
def test_get_hip_save_version_from_file(mocker, shared_datadir, hip_name, expected):
    """Test houdini_core_tools.hip_file.get_hip_save_version_from_file()."""
    mock_value = "20.5.493" if hip_name is not None else None
    mocker.patch("houdini_core_tools.hip_file._get_global_variable_value_from_file", return_value=mock_value)

    hip_path = shared_datadir / "test_hip_saved_data.hiplc"

    result = hip_file.get_hip_save_version_from_file(hip_path)

    assert result == expected

    result = hip_file.get_hip_save_version_from_file(hip_path.as_posix())

    assert result == expected


@pytest.mark.usefixtures("clear_hip_file")
@pytest.mark.parametrize(
    "hip_name,expected",
    (
        ("test_hip_saved_data.hiplc", datetime.datetime(2025, 2, 5, 5, 33, 57)),
        (None, None),
    ),
)
def test_hip_save_time(shared_datadir, hip_name, expected):
    """Test houdini_core_tools.hip_file.hip_save_time()."""
    if hip_name is not None:
        hou.hipFile.load((shared_datadir / hip_name).as_posix(), suppress_save_prompt=True, ignore_load_warnings=True)

    result = hip_file.hip_save_time()

    assert result == expected


@pytest.mark.usefixtures("clear_hip_file")
@pytest.mark.parametrize(
    "hip_name,expected",
    (
        ("test_hip_saved_data.hiplc", (20, 5, 493)),
        (None, None),
    ),
)
def test_hip_save_version(shared_datadir, hip_name, expected):
    """Test houdini_core_tools.hip_file.hip_save_version()."""
    if hip_name is not None:
        hou.hipFile.load((shared_datadir / hip_name).as_posix(), suppress_save_prompt=True, ignore_load_warnings=True)

    result = hip_file.hip_save_version()

    assert result == expected


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
