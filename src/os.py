"""
This is a module docstring
"""


import getpass
import platform


class OS:
    """This class provides information about the operating system and user."""

    def __init__(self):
        """variables"""
        self.current_user = self.get_current_user()
        self.windows = self.is_windows()
        self.linux = self.is_linux()

    def _get_os_name(self):
        """This private method returns the name of the current operating system."""
        return platform.system()

    def is_windows(self):
        """This method checks if the current operating system is Windows."""
        return self._get_os_name() == "Windows"

    def is_linux(self):
        """This method checks if the current operating system is Linux."""
        return self._get_os_name() == "Linux"

    def get_current_user(self):
        """This method returns the name of the current user."""
        return getpass.getuser()
