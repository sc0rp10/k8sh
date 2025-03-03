from abc import ABC, abstractmethod
from typing import List, Optional

from state.state import State
from utils.terminal import Color, colorize


class Command(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the command"""
        pass

    @abstractmethod
    def get_help(self) -> str:
        """Get the help text for the command"""
        pass

    def has_path_completion(self) -> bool:
        return False

    def get_aliases(self) -> List[str]:
        """Get the aliases for the command"""
        return []

    def get_usage(self) -> str:
        """Get the extended usage information for the command"""
        return f"{colorize('Usage:', Color.BRIGHT_GREEN)} {colorize(self.get_name(), Color.BRIGHT_YELLOW)} {colorize('[arguments]', Color.BRIGHT_CYAN)}"

    def execute(self, state: State, args: List[str]) -> None:
        pass


class GenericCommand(Command):
    """Command that works both with files and directories"""
    pass


class DirectoryCommand(Command):
    """Command that works only with directories"""

    @abstractmethod
    def _do_execute(self, state: State, directory: str, args: List[str]) -> None:
        """Execute the command"""
        pass

    @abstractmethod
    def _get_directory(self, args: List[str]) -> Optional[str]:
        """Parse directory name from args. Raise an exception otherwise"""
        pass

    def has_path_completion(self) -> bool:
        return True

    def execute(self, state: State, args: List[str]) -> None:
        directory = self._get_directory(args)

        if directory is None:
            raise Exception()

        self._do_execute(state, directory, args)


class FileCommand(Command):
    """Command that works only with files"""

    def execute(self, state: State, args: List[str]) -> None:
        filename = self._get_filename(args)

        if filename is None:
            raise Exception()

        current_path = state.get_current_path()

        if not filename.startswith('/'):
            filename = f"/{current_path}/{filename}"

        path_components = filename.strip('/').split('/')

        if len(path_components) == 1:
            # This is a namespace at root level
            namespace = ""
            resource_type = "namespace"
            resource_name = path_components[0]
        elif len(path_components) == 2:
            # This is a resource type at namespace level
            namespace = path_components[0]
            resource_type = path_components[1]
            resource_name = ""
        elif len(path_components) == 3:
            # Normal case: /namespace/resource_type/resource_name
            namespace = path_components[0]
            resource_type = path_components[1]
            resource_name = path_components[2]
        elif len(path_components) == 4:
            # Extended case: /namespace/resource_type/resource_name/pod_name
            # This is for accessing a specific pod of a deployment or other workload controller
            namespace = path_components[0]
            resource_type = path_components[1]
            # Combine the resource name and pod name with a slash
            resource_name = f"{path_components[2]}/{path_components[3]}"
        else:
            raise Exception(f"Error: Invalid path format: {filename}")

        self._do_execute(state, namespace, resource_type, resource_name)

    def has_path_completion(self) -> bool:
        return True

    @abstractmethod
    def _do_execute(self, state: State, namespace: str, resource_type: str, resource_name: str) -> None:
        """Execute the command"""
        pass

    @abstractmethod
    def _get_filename(self, args: List[str]) -> Optional[str]:
        """Parse filename from args. Raise an exception otherwise"""
        pass
