#!/usr/bin/env python3
"""
Clear command for K8sh
"""
import os
import platform
import subprocess
from typing import List

from command.base import GenericCommand
from state.state import State


class ClearCommand(GenericCommand):
    """Command to clear the terminal screen"""

    def get_name(self) -> str:
        """Get the name of the command"""
        return "clear"

    def get_aliases(self) -> List[str]:
        """Get the aliases for the command"""
        return ["cls"]

    def get_help(self) -> str:
        """Get the help text for the command"""
        return "Clear the terminal screen"

    def get_usage(self) -> str:
        """Get the usage text for the command"""
        return "Usage: clear\n       cls\n\nClears the terminal screen."

    def execute(self, state: State, args: List[str]) -> None:
        """Execute the clear command"""
        # Different clear commands based on OS
        if platform.system() == "Windows":
            os.system("cls")
        else:
            # For Unix-like systems (Linux, macOS)
            # Using ANSI escape sequence as a fallback
            print("\033c", end="")

            # Also try the clear command if available
            try:
                subprocess.run(["clear"], check=False)
            except FileNotFoundError:
                # If clear command is not available, we've already used the ANSI escape sequence
                pass
