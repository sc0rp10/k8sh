from typing import List, Optional

from command.base import DirectoryCommand
from state.state import State
from utils.terminal import Color, colorize


class CdCommand(DirectoryCommand):
    """Command to change the current directory"""

    def get_name(self) -> str:
        """Get the name of the command"""
        return "cd"

    def get_aliases(self) -> List[str]:
        """Get the aliases for the command"""
        return ["chdir"]

    def get_help(self) -> str:
        """Get the help text for the command"""
        return "Change the current directory"

    def get_usage(self) -> str:
        """Get the extended usage information for the command"""
        cmd = colorize("cd", Color.BRIGHT_YELLOW)
        chdir_cmd = colorize("chdir", Color.BRIGHT_YELLOW)
        directory = colorize("[directory]", Color.BRIGHT_CYAN)

        usage = [
            f"{colorize('Usage:', Color.BRIGHT_GREEN)} {cmd} {directory}",
            f"       {chdir_cmd} {directory}",
            "",
            f"{colorize('Examples:', Color.BRIGHT_GREEN)}",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Change to root directory",
            f"  {cmd} {colorize('/', Color.BRIGHT_BLUE)}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Change to a namespace",
            f"  {cmd} {colorize('default', Color.BRIGHT_BLUE)}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Change to a resource type within a namespace",
            f"  {cmd} {colorize('default', Color.BRIGHT_BLUE)}/{colorize('pods', Color.BRIGHT_GREEN)}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Change to parent directory",
            f"  {cmd} {colorize('..', Color.BRIGHT_BLUE)}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Change to previous directory",
            f"  {cmd} {colorize('-', Color.BRIGHT_BLUE)}",
            "",
            f"{colorize('Notes:', Color.BRIGHT_GREEN)}",
            f"  - If no directory is specified, changes to the {colorize('root directory', Color.BRIGHT_BLUE)}",
            f"  - Supports both {colorize('absolute paths', Color.BRIGHT_CYAN)} (starting with /) and {colorize('relative paths', Color.BRIGHT_CYAN)}",
            f"  - Use {colorize('cd ..', Color.BRIGHT_YELLOW)} to navigate up one level",
            f"  - Use {colorize('cd -', Color.BRIGHT_YELLOW)} to navigate to the previous directory",
        ]
        return "\n".join(usage)

    def _get_directory(self, args: List[str]) -> Optional[str]:
        """Parse directory name from args"""
        if not args:
            return "/"

        return args[0]

    def _do_execute(self, state: State, directory: str, args: List[str]) -> None:
        """Execute the cd command"""

        if directory == "-":
            previous_path = state.get_previous_path()
            if previous_path is None or previous_path == "":
                print(colorize("Error: No previous directory", Color.BRIGHT_RED))
                return

            # Store the current path temporarily to swap with previous path
            current_path = state.get_current_path()

            # For the cd - command, we need to handle the path swapping properly
            try:
                # In this implementation, we properly swap the current and previous paths
                # We'll store the current path as previous, and set the previous as current

                # Set previous_path first to ensure it's preserved before any changes
                temp_previous = previous_path
                # Update the previous path to the current path
                state.previous_path = current_path

                # Now set the current path to what was previously stored
                # Handle root path as a special case
                if temp_previous == "/":
                    # For root, we'll use the manager's set_path which properly handles root
                    # We can safely use "/" here because set_path knows how to handle it
                    state.path_manager.set_path("/")
                else:
                    # For any other path, use the normal path setting mechanism
                    # This ensures proper validation and handling of the path
                    # We use proper path management API instead of directly manipulating _path
                    state.path_manager.set_path(temp_previous)
            except Exception as e:
                print(colorize(f"Error navigating to previous directory: {str(e)}", Color.BRIGHT_RED))
                # Restore the previous state if there was an error
                state.previous_path = previous_path
            return

        # Normalize directory path by removing any double slashes
        directory = directory.replace('//', '/')

        # Remove trailing slash if present
        if directory.endswith('/') and directory != '/':
            directory = directory[:-1]

        try:
            # Handle absolute paths
            if directory.startswith('/'):
                # Set the path directly
                state.set_path(directory)
            elif directory == "..":
                # Go up one level
                state.set_path("..")
            elif '/' in directory:
                # Handle paths with slashes (like default/services)
                # Get current path and combine with directory
                current_path = state.get_current_path()

                # If we're at root, just use the directory
                if not current_path:
                    state.set_path(directory)
                else:
                    # Combine current path with directory
                    new_path = current_path + "/" + directory
                    # Normalize path by removing any double slashes
                    new_path = new_path.replace('//', '/')
                    state.set_path(new_path)
            else:
                # Check if the directory exists
                if not state.is_directory(directory):
                    print(colorize(f"Error: Cannot cd to '{directory}': Not a directory", Color.BRIGHT_RED))
                    return

                # Add the segment to the path
                state.add_path_segment(directory)
        except Exception as e:
            print(colorize(f"Error executing command: {str(e)}", Color.BRIGHT_RED))
