from typing import List

from command.base import Command
from state.state import State
from utils.terminal import Color, colorize


class ExitCommand(Command):
    """Command to exit the shell"""

    def get_name(self) -> str:
        """Get the name of the command"""
        return "exit"

    def get_aliases(self) -> List[str]:
        """Get the aliases for the command"""
        return ["quit", "bye", "q"]

    def get_help(self) -> str:
        """Get the help text for the command"""
        return "Exit the shell"

    def get_usage(self) -> str:
        """Get the extended usage information for the command"""
        exit_cmd = colorize("exit", Color.BRIGHT_YELLOW)
        quit_cmd = colorize("quit", Color.BRIGHT_YELLOW)
        bye_cmd = colorize("bye", Color.BRIGHT_YELLOW)
        q_cmd = colorize("q", Color.BRIGHT_YELLOW)

        usage = [
            f"{colorize('Usage:', Color.BRIGHT_GREEN)} {exit_cmd}",
            f"       {quit_cmd}",
            f"       {bye_cmd}",
            f"       {q_cmd}",
            "",
            f"{colorize('Examples:', Color.BRIGHT_GREEN)}",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Exit the shell",
            f"  {exit_cmd}",
            "",
            f"{colorize('Notes:', Color.BRIGHT_GREEN)}",
            "  - This command takes no arguments",
            "  - Any of the aliases can be used to exit the shell",
        ]
        return "\n".join(usage)

    def execute(self, state: State, args: List[str]) -> None:
        """Execute the exit command"""
        print(colorize("Exiting shell...", Color.BRIGHT_MAGENTA))
        raise SystemExit(0)
