"""Houdini related context managers."""

# Future
from __future__ import annotations

# Standard Library
from collections.abc import Iterable
from contextlib import ContextDecorator, contextmanager
from typing import TYPE_CHECKING, Generator  # , Iterable

# Houdini
import hou

if TYPE_CHECKING:
    from types import TracebackType


# Classes


class emit_varchange(ContextDecorator):
    """Emit a varchange call at the end of the scope.

    In the event of nested uses, only the outermost will execute the varchange.

    >>> with emit_varchange():
    ...     hou.hscript("set FOO=456")
    ...
    >>> # A varchange call will have been emitted for FOO.
    """

    _ACTIVE = False

    def __init__(self) -> None:
        self._should_run = False

    def __enter__(self) -> None:
        self._should_run = not emit_varchange._ACTIVE

        if self._should_run:
            emit_varchange._ACTIVE = True

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._should_run:
            hou.hscript("varchange")
            emit_varchange._ACTIVE = False


class temporarily_unlock_parameters(ContextDecorator):
    """Context manager to temporarily unlock parameters and re-lock them on exit.

    >>> my_parameter = hou.parm("/obj/geo1/scale")
    >>> with temporarily_unlock_parameters(my_parameter):
    ...     my_parameter.set(3)
    ...

    Args:
        parms_to_unlock: The parameter(s) to unlock.
    """

    def __init__(self, parms_to_unlock: hou.Parm | hou.ParmTuple | Iterable[hou.Parm]) -> None:
        # If the item is a parm tuple then convert it to its constituent hou.Parm
        # objects.
        if isinstance(parms_to_unlock, hou.ParmTuple):
            parms_to_unlock = tuple(parms_to_unlock)  # type: ignore

        if not isinstance(parms_to_unlock, Iterable):
            parms_to_unlock = [parms_to_unlock]

        self.parms = parms_to_unlock
        # Store the current status, so we can restore it if necessary.
        self.locked_states = [parm.isLocked() for parm in parms_to_unlock]

    def __enter__(self) -> None:
        self._set_lock_state(locked=False)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._set_lock_state(locked=True)

    def _set_lock_state(self, *, locked: bool) -> None:
        """Set the parms lock states to the desired value, if necessary.

        Args:
            locked: Whether the parms should be locked.
        """
        for parm, parm_is_locked in zip(self.parms, self.locked_states):
            if parm_is_locked:
                try:
                    parm.lock(locked)

                # This might be raised if the parameter is inside a locked HDA
                # or not included in a take. Since Houdini messages never contain
                # useful information like the offending parameter we'll re-raise
                # an exception with a better message.
                except hou.PermissionError as inst:
                    raise hou.PermissionError(  # noqa: TRY003
                        f"Error setting lock status for {parm.path()}"
                    ) from inst


# Functions


@contextmanager
def restore_current_selection() -> Generator[None, None, None]:
    """Restore the current selection after the block has exited.

    The selection will be restored in the event an exception occurs inside
    the block.

    >>> with restore_current_selection():
    ...     # Perform actions that could change the selection.
    ...
    """
    # Stash for restoring afterwards.
    selected = hou.selectedItems()

    hou.clearAllSelected()

    try:
        yield

    # Use finally so the selection is always restored even if errors occur.
    finally:
        hou.clearAllSelected()

        # Restore the selection.
        for item in selected:
            item.setSelected(True)


@contextmanager
def set_temporary_update_mode(
    update_mode: hou.updateMode,
) -> Generator[None, None, None]:
    """Temporarily set the UI update mode for the scope of the block.

    The update mode will be restored in the event an exception occurs inside
    the block.

    >>> with set_temporary_update_mode(hou.updateMode.Manual):
    ...     # Perform actions while in manual mode.
    ...

    Args:
        update_mode: The temporary update mode.
    """
    # Get the current update mode to restore it after.
    current_mode = hou.updateModeSetting()

    hou.setUpdateMode(update_mode)  # type: ignore

    try:
        yield

    finally:
        # Restore the previous update mode.
        hou.setUpdateMode(current_mode)
