"""
RetroScope

Parameter Registry

Stores all runtime-adjustable parameters.

Parameters are shared engine state and can be modified by:

- Web UI
- Keyboard shortcuts
- Plugins
- Automation
- Future scripting

Modules should READ parameters.

They should never own global configuration.
"""

from __future__ import annotations


class ParameterRegistry:

    def __init__(self):

        self._values = {}

    # ---------------------------------------------------------

    def set(
        self,
        name: str,
        value,
    ) -> None:

        self._values[name] = value

    # ---------------------------------------------------------

    def get(
        self,
        name: str,
        default=None,
    ):

        return self._values.get(
            name,
            default,
        )

    # ---------------------------------------------------------

    def exists(
        self,
        name: str,
    ) -> bool:

        return name in self._values

    # ---------------------------------------------------------

    def remove(
        self,
        name: str,
    ) -> None:

        self._values.pop(
            name,
            None,
        )

    # ---------------------------------------------------------

    def clear(self):

        self._values.clear()

    # ---------------------------------------------------------

    def names(self):

        return tuple(
            sorted(self._values.keys())
        )