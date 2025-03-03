from typing import List

from command.base import Command
from command.registry import CommandRegistry
from state.state import State
from utils.terminal import Color, colorize


class HelpCommand(Command):
    """Command to display help information"""

    def __init__(self, command_registry: CommandRegistry) -> None:
        self._command_registry = command_registry

    def get_name(self) -> str:
        """Get the name of the command"""
        return "help"

    def get_aliases(self) -> List[str]:
        """Get the aliases for the command"""
        return ["?"]

    def get_help(self) -> str:
        """Get the help text for the command"""
        return "Display help information for available commands"

    def get_usage(self) -> str:
        """Get the extended usage information for the command"""
        help_cmd = colorize("help", Color.BRIGHT_YELLOW)
        command_arg = colorize("<command>", Color.BRIGHT_CYAN)

        usage = [
            f"{colorize('Usage:', Color.BRIGHT_GREEN)} {help_cmd} [{command_arg}]",
            "",
            f"{colorize('Examples:', Color.BRIGHT_GREEN)}",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Display help for all commands",
            f"  {help_cmd}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Display help for a specific command",
            f"  {help_cmd} {colorize('ls', Color.BRIGHT_YELLOW)}",
            f"  {help_cmd} {colorize('cd', Color.BRIGHT_YELLOW)}",
            "",
            f"{colorize('Notes:', Color.BRIGHT_GREEN)}",
            "  - Without arguments, lists all available commands",
            "  - With a command name, shows detailed help for that command",
            f"  - You can also use {colorize('?', Color.BRIGHT_YELLOW)} as an alias for {help_cmd}",
        ]
        return "\n".join(usage)

    def execute(self, state: State, args: List[str]) -> None:
        """Execute the help command"""
        if args and args[0]:
            # Show help for a specific command
            command_name = args[0]
            command = self._command_registry.get_command(command_name)

            if command:
                print(f"{colorize('Command:', Color.BRIGHT_GREEN)} {colorize(command.get_name(), Color.BRIGHT_YELLOW)}")
                aliases = command.get_aliases()
                if aliases:
                    print(f"{colorize('Aliases:', Color.BRIGHT_GREEN)} {colorize(', '.join(aliases), Color.BRIGHT_YELLOW)}")
                print(f"{colorize('Description:', Color.BRIGHT_GREEN)} {command.get_help()}")
                print(f"\n{command.get_usage()}")
            else:
                print(colorize(f"Command '{command_name}' not found", Color.BRIGHT_RED))
        else:
            # Show help for all commands
            print(colorize("Available commands:", Color.BRIGHT_GREEN))
            for command in self._command_registry.get_all_commands():
                name = colorize(command.get_name(), Color.BRIGHT_YELLOW)
                aliases_help = f"({colorize(', '.join(command.get_aliases()), Color.BRIGHT_BLUE)})" if command.get_aliases() else ""
                print(f"  {name} {aliases_help}: {command.get_help()}")
            print(f"\nType {colorize('help <command>', Color.BRIGHT_YELLOW)} for more information on a specific command.")
