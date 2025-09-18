"""Functions related to hip files."""

# Future
from __future__ import annotations

# Standard Library
import datetime
import functools
import pathlib
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

# Houdini
import hou

# Non-Public Functions


def _get_global_variable_value_from_file(hip_file: pathlib.Path, variable_name: str) -> str | None:
    """Parse a hip file and attempt to determine a global variable value.

    This will quickly check the start of the file for the definition of the
    global variable name global variable and return its value if found.

    Args:
        hip_file: The hip file to parse.
        variable_name: The global variable name to look for.

    Returns:
        The determined save version, if any.
    """
    version = None

    # We need to ignore errors otherwise the magic bits in the hip file will cause
    # failures. Those don't occur on lines we care about so it's safe to ignore them.
    with hip_file.open("r", encoding="utf-8", errors="ignore") as handle:
        # Sentinel to know if we've found any global variable definitions yet.
        found_globals = False

        while line := handle.readline():  # pragma: no branch
            cleaned_line = line.strip()

            if cleaned_line.startswith("set -g"):
                # Flag that we've found global definitions so that we can bail out reading
                # the file after the section.
                found_globals = True

                result = re.match(f"set -g {variable_name} = '(.+)'", cleaned_line)
                if result is not None:
                    version = result.group(1)
                    break

            # If we didn't find a global variable definition on the line but have found some
            # previously then we are done and should stop reading the file.
            elif found_globals:
                break

    return version


# Functions


def check_unsaved_changes(*, prompt: bool = False) -> Callable:
    """Function decorator ensures there are no unsaved changes in the session.

    Args:
        prompt: Whether to prompt the user to save the hip file.

    Returns:
        The wrapped function.
    """

    def decorator(func):  # type: ignore
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # type: ignore
            if hou.hipFile.hasUnsavedChanges():
                if hou.isUIAvailable() and prompt:
                    choice = hou.ui.displayCustomConfirmation(
                        "Hip file has unsaved changes",
                        buttons=("Yes", "No"),
                        severity=hou.severityType.Warning,
                        close_choice=1,
                        help="Would you like to save and proceed?",
                        title="Unsaved changes",
                    )

                    if choice == 0:
                        hou.hipFile.save()

                    else:
                        raise hou.OperationFailed("Hip file save declined")  # noqa: TRY003

                else:
                    raise hou.OperationFailed("Hip file has unsaved changes")  # noqa: TRY003

            # Return the wrapped function result.
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_hip_save_time_from_file(hip_path: pathlib.Path | str) -> datetime.datetime | None:
    """Get the time the hip file was last saved.

    This function uses the value of $_HIP_SAVETIME stored in the file.

    Returns:
        The time the hip file was last saved, if any.
    """
    if isinstance(hip_path, str):
        hip_path = pathlib.Path(hip_path)

    value = _get_global_variable_value_from_file(hip_path, "_HIP_SAVETIME")

    if not value:
        return None

    return datetime.datetime.strptime(value, "%a %b %d %H:%M:%S %Y")


def get_hip_save_version_from_file(hip_path: pathlib.Path | str) -> tuple[int, ...] | None:
    """Get the version of Houdini last used to save the hip file.

    This function uses the value of $_HIP_SAVEVERSION stored in the file.

    Returns:
        The Houdini version last used to save the hip file, if any.
    """
    if isinstance(hip_path, str):
        hip_path = pathlib.Path(hip_path)

    value = _get_global_variable_value_from_file(hip_path, "_HIP_SAVEVERSION")

    if not value:
        return None

    return tuple(int(component) for component in value.split("."))


def hip_save_time() -> datetime.datetime | None:
    """Get the time the current hip file was last saved.

    This function uses the value of $_HIP_SAVETIME.

    Returns:
        The time the hip file was last saved, if any.
    """
    value = hou.text.expandString("$_HIP_SAVETIME")

    if not value:
        return None

    return datetime.datetime.strptime(value, "%a %b %d %H:%M:%S %Y")


def hip_save_version() -> tuple[int, ...] | None:
    """Get the version of Houdini last used to save the current hip file.

    This function uses the value of $_HIP_SAVEVERSION.

    Returns:
        The Houdini version last used to save the hip file, if any.
    """
    value = hou.text.expandString("$_HIP_SAVEVERSION")

    if not value:
        return None

    return tuple(int(component) for component in value.split("."))


def hip_version() -> str | None:
    """Get the major version of the current hip file.

    Returns None if the version could not be determined.

    Returns:
        The hip file version, if any.
    """
    # Look for "v#".
    pattern = re.compile(r"v(\d*)", re.IGNORECASE)

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
