from typing import Dict, List, Optional

from command.base import Command


class CommandRegistry:
    """Registry for all available commands"""

    def __init__(self) -> None:
        self._commands: Dict[str, Command] = {}
        self._aliases: Dict[str, str] = {}

    def register_command(self, command_instance: Command) -> None:
        """Register a command instance"""
        # Get the command name using the classmethod
        command_name = command_instance.get_name()

        # Register the main command name
        self._commands[command_name] = command_instance

        # Register aliases using the classmethod
        for alias in command_instance.get_aliases():
            self._aliases[alias] = command_name

    def get_command(self, name: str) -> Optional[Command]:
        """Get a command by name or alias"""
        # Check if it's a direct command name
        if name in self._commands:
            return self._commands[name]

        # Check if it's an alias
        if name in self._aliases:
            return self._commands[self._aliases[name]]

        return None

    def get_all_commands(self) -> List[Command]:
        """Get all registered commands"""
        return list(self._commands.values())

    def get_command_names(self) -> List[str]:
        """Get all command names and aliases"""
        return list(self._commands.keys()) + list(self._aliases.keys())

    def get_for_autocomplete(self) -> List[str]:
        commands = []

        for _, command in self._commands.items():
            if command.has_path_completion():
                commands.append(command.get_name())

                for alias in command.get_aliases():
                    commands.append(alias)

        return commands
