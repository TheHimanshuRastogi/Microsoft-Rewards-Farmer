"""
This is a module docstring
"""

import os
import platform


class Os:
    """This class provides information about the operating system and user."""

    def __init__(self) -> None:
        """variables"""
        self.windows = self.is_windows()
        self.linux = self.is_linux()

    def _get_os_name(self) -> str:
        """This private method returns the name of the current operating system."""
        return platform.system()

    def is_windows(self) -> bool:
        """This method checks if the current operating system is Windows."""
        return self._get_os_name() == "Windows"

    def is_linux(self) -> bool:
        """This method checks if the current operating system is Linux."""
        return self._get_os_name() == "Linux"

    def env(self, env: str) -> None|str:
        """This method is to get ENV value."""
        return None if os.environ.get(env) == "None" else os.environ.get(env)
    
