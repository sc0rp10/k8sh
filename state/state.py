from typing import List, Optional, Union, Any

from state.path_manager import Manager


class State:
    """Represents the application state"""

    def __init__(self) -> None:
        self.path_manager = Manager()
        self.current_command: Optional[str] = None
        self.prompt_session: Optional[Any] = None
        # Initialize previous_path to root ("/") so we can navigate back to root from first directory
        self.previous_path: str = "/"

    def get_current_path(self) -> str:
        """Get the current path"""
        return self.path_manager.get_full_path()

    def set_path(self, path: str) -> None:
        """Set the current path"""
        # Store current path as previous path before changing
        self.previous_path = self.get_current_path()
        self.path_manager.set_path(path)

    def add_path_segment(self, segment: str) -> None:
        """Add a segment to the current path"""
        self.path_manager.add_segment(segment)

    def is_directory(self, path_segment: str) -> bool:
        """Check if a path segment is a directory"""
        return self.path_manager.is_directory(path_segment)

    def get_available_items(self) -> Optional[Union[List[str], str]]:
        """Get available items at the current path"""
        return self.path_manager.get_available_values()

    def set_current_command(self, command: Optional[str]) -> None:
        """Set the current command"""
        self.current_command = command

    def get_current_command(self) -> Optional[str]:
        """Get the current command"""
        return self.current_command

    def set_prompt_session(self, session: Any) -> None:
        """Set the prompt session"""
        self.prompt_session = session

    def get_prompt_session(self) -> Optional[Any]:
        """Get the prompt session"""
        return self.prompt_session

    def get_previous_path(self) -> Optional[str]:
        """Get the previous path"""
        return self.previous_path

    def set_previous_path(self, path: str) -> None:
        """Set the previous path"""
        self.previous_path = path
