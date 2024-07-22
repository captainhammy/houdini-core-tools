"""Functions related to hip files."""

# Future
from __future__ import annotations

# Standard Library
import pathlib
import re

# Houdini
import hou

# Functions


def hip_version() -> str | None:
    """Get the major version of the current hip file.

    Returns None if the version could not be determined.

    Returns:
        The hip file version, if any.
    """
    # Look for "v#".
    pattern = re.compile("v(\\d*)", re.IGNORECASE)

    # Try to find any matches.
    result = pattern.findall(hou.hipFile.name())

    if not result:
        return None

    # Return a 0 padded string
    return f"{int(result[-1]):02d}"


def save_copy(file_path: str | pathlib.Path) -> None:
    """Save a copy of the current session without saving to the current hip file.

    Args:
        file_path: The target file path.
    """
    if isinstance(file_path, pathlib.Path):
        file_path = file_path.as_posix()

    current_name = hou.hipFile.name()

    # Save the hip file to the target name. We don't want to add the new file to the
    # list of recent files.
    hou.hipFile.save(file_path, save_to_recent_files=False)

    # Restore the original name.
    hou.hipFile.setName(current_name)


def set_frame_range(start: float, end: float) -> None:
    """Set the current frame range.

    If the current frame is not within the new range it will be updated to the
    start frame.

    Args:
        start: The start frame.
        end: The end frame.
    """
    # Set the start and end frames for both the timeline and playback range.
    hou.playbar.setFrameRange(start, end)
    hou.playbar.setPlaybackRange(start, end)

    # If the current frame isn't within the new range, set the current frame to
    # the start frame.
    if not start <= hou.frame() <= end:
        hou.setFrame(start)
