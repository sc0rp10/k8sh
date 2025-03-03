from typing import List

from command.base import GenericCommand
from state.state import State
from utils.terminal import format_long_listing, Color, colorize


class LsCommand(GenericCommand):
    """Command to list the contents of the current directory or a specified directory"""

    def get_name(self) -> str:
        """Get the name of the command"""
        return "ls"

    def get_aliases(self) -> List[str]:
        """Get the aliases for the command"""
        return ["list", "dir", "ll"]

    def get_help(self) -> str:
        """Get the help text for the command"""
        return "List the contents of the current directory or a specified directory"

    def has_path_completion(self) -> bool:
        return True

    def get_usage(self) -> str:
        """Get the extended usage information for the command"""
        cmd = colorize("ls", Color.BRIGHT_YELLOW)
        list_cmd = colorize("list", Color.BRIGHT_YELLOW)
        dir_cmd = colorize("dir", Color.BRIGHT_YELLOW)
        directory = colorize("[directory]", Color.BRIGHT_CYAN)

        usage = [
            f"{colorize('Usage:', Color.BRIGHT_GREEN)} {cmd} {directory}",
            f"       {list_cmd} {directory}",
            f"       {dir_cmd} {directory}",
            "",
            f"{colorize('Examples:', Color.BRIGHT_GREEN)}",
            f"  {colorize('#', Color.BRIGHT_BLACK)} List contents of the current directory",
            f"  {cmd}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} List contents of the root directory",
            f"  {cmd} {colorize('/', Color.BRIGHT_BLUE)}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} List contents of a resource type within a namespace",
            f"  {cmd} {colorize('default', Color.BRIGHT_BLUE)}/{colorize('pods', Color.BRIGHT_GREEN)}",
            "",
            f"{colorize('Notes:', Color.BRIGHT_GREEN)}",
            f"  - If no directory is specified, lists the contents of the {colorize('current directory', Color.BRIGHT_BLUE)}",
            f"  - Supports both {colorize('absolute paths', Color.BRIGHT_CYAN)} (starting with /) and {colorize('relative paths', Color.BRIGHT_CYAN)}",
            "  - Displays items in a simplified format with type, date, and name",
        ]
        return "\n".join(usage)

    def _parse_args(self, args: List[str]) -> str:
        """Parse command arguments

        Returns:
            str: path
        """
        # If there are arguments, the first one is the path
        return args[0] if args else ""

    def execute(self, state: State, args: List[str]) -> None:
        """Execute the ls command"""
        # Parse arguments
        path = self._parse_args(args)

        # If a path is provided, temporarily change to that path to list its contents
        if path:
            # Save current path
            current_path = state.get_current_path()

            try:
                # Try to set the path to the provided argument
                state.set_path(path)

                # Get available items at the new path
                items = state.get_available_items()

                # Print the items
                if items:
                    if isinstance(items, list):
                        # Always use long listing format
                        print(format_long_listing(items, lambda item: state.is_directory(f"{state.get_current_path()}/{item}")))
                    else:
                        print(items)
                else:
                    print("No items found")

                # Restore original path by directly setting the path manager's internal state
                # This avoids validation errors when restoring the path
                state.path_manager._path = current_path.split("/") if current_path else []
                # Update the previous_path in the state to maintain proper cd - functionality
                state.previous_path = path
            except Exception as e:
                # Restore original path on error by directly setting the path manager's internal state
                state.path_manager._path = current_path.split("/") if current_path else []
                print(f"Error: {str(e)}")
        else:
            # List contents of current directory
            items = state.get_available_items()

            # Print the items
            if items:
                if isinstance(items, list):
                    # Always use long listing format
                    print(format_long_listing(items, lambda item: state.is_directory(f"{state.get_current_path()}/{item}")))
                else:
                    print(items)
            else:
                print("No items found")
