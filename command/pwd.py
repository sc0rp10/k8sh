from typing import List

from command.base import Command
from state.state import State
from utils.terminal import Color, colorize


class PwdCommand(Command):
    """Command to print the current working directory"""

    def get_name(self) -> str:
        """Get the name of the command"""
        return "pwd"

    def get_aliases(self) -> List[str]:
        """Get the aliases for the command"""
        return []

    def get_help(self) -> str:
        """Get the help text for the command"""
        return "Print the current working directory"

    def get_usage(self) -> str:
        """Get the extended usage information for the command"""
        pwd_cmd = colorize("pwd", Color.BRIGHT_YELLOW)

        usage = [
            f"{colorize('Usage:', Color.BRIGHT_GREEN)} {pwd_cmd}",
            "",
            f"{colorize('Examples:', Color.BRIGHT_GREEN)}",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Print the current working directory",
            f"  {pwd_cmd}",
            "",
            f"{colorize('Notes:', Color.BRIGHT_GREEN)}",
            "  - This command takes no arguments",
            f"  - The output is the full path of the current location in the {colorize('virtual filesystem', Color.BRIGHT_MAGENTA)}",
        ]
        return "\n".join(usage)

    def execute(self, state: State, args: List[str]) -> None:
        """Execute the pwd command"""
        path = state.get_current_path()
        # If path is empty, print empty string
        if not path:
            print("")
            return

        # Colorize the path components
        parts = path.split('/')
        colored_parts = []
        for part in parts:
            if part:  # Skip empty parts
                colored_parts.append(colorize(part, Color.BRIGHT_BLUE))
        colored_path = '/'.join(colored_parts)
        print(colored_path)
