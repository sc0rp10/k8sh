import os
import sys
from typing import List, Dict, Callable, Optional, Union

from k8s_client import get_kubernetes_client

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Initialize Kubernetes client
k8s_client = get_kubernetes_client()

# Define the structure of the virtual filesystem
available_segments: List[Dict[str, Callable[..., Optional[Union[List[str], str]]]]] = [
    {
        # Level 0: Namespaces
        "children": lambda _=None: k8s_client.get_namespaces(),
    },
    {
        # Level 1: Resource types
        "children": lambda _=None: k8s_client.get_resource_types(),
    },
    {
        # Level 2: Resources of a specific type in a namespace
        "children": lambda namespace, resource_type: k8s_client.get_resources(namespace, resource_type),
    },
    {
        # Level 3: If resource type is a workload controller (deployment, statefulset, etc.),
        # show its pods. For pods, show containers.
        "children": lambda namespace, resource_type, resource_name: (
            k8s_client.get_pods_for_resource(namespace, resource_type, resource_name)
            if k8s_client.is_resource_with_children(resource_type) and resource_type != "pods"
            else k8s_client.get_pod_containers(namespace, resource_name)
            if resource_type == "pods"
            else None
        ),
    },
    {
        # Level 4: For pods of a workload controller, show containers
        "children": lambda namespace, resource_type, resource_name, pod_name: (
            k8s_client.get_pod_containers(namespace, pod_name)
            if k8s_client.is_resource_with_children(resource_type) and resource_type != "pods"
            else None
        ),
    },
]

# Define which levels contain files vs directories
# Level 2 (specific resources) are files unless they're workload controllers or pods
# Level 3 (pods) are files unless they're from workload controllers
# Level 4 (containers) are always files
file_levels = [4]  # Container level is always files


class Manager:
    """Manages the virtual filesystem path"""

    def __init__(self) -> None:
        self._path: List[str] = []

    def get_full_path(self) -> str:
        """Get the full path as a string"""
        return "/".join(self._path) if self._path else ""

    def get_available_values(self) -> Optional[Union[List[str], str]]:
        """Get available values at the current path level"""
        if len(self._path) >= len(available_segments):
            return None
        return available_segments[len(self._path)]["children"](*self._path)

    def is_directory(self, segment: str) -> bool:
        """Check if a segment is a directory at the current level"""
        # Get the current level
        current_level = len(self._path)

        # If we're at a known file level, items are files
        if current_level in file_levels:
            return False

        # Special case for level 2 (resources)
        if current_level == 2:
            # Workload controllers and pods have children
            return k8s_client.is_resource_with_children(self._path[1])

        # Special case for level 3 (pods or containers)
        if current_level == 3:
            # If parent is a pod, this is a container (file)
            if self._path[1] == "pods":
                return False
            # If parent is a workload controller, this is a pod (directory)
            return True

        # By default, consider it a directory
        return True

    def add_segment(self, segment: str) -> None:
        """Add a segment to the path"""
        available_values = self.get_available_values()

        if available_values is None:
            raise Exception("Invalid segment")

        if isinstance(available_values, list) and segment in available_values:
            self._path.append(segment)
        elif isinstance(available_values, str) and segment == available_values:
            self._path.append(segment)
        else:
            raise Exception(f"Invalid segment {segment}")

    def set_path(self, path: str) -> None:
        """Set the path from a string"""
        # Fix double slashes in the path
        while '//' in path:
            path = path.replace('//', '/')

        if path == "/":
            self._path = []
            return

        if path == "..":
            if len(self._path) > 0:
                self._path.pop()
            return

        # Handle absolute paths (starting with /) by resetting the path
        if path.startswith("/"):
            self._path = []
            path = path[1:]  # Remove leading slash

            # If path is empty after removing the leading slash, return
            if not path:
                return

        # Split the path into segments
        segments = path.split("/")

        # Create a temporary path to validate each segment
        temp_path = self._path.copy()
        valid_segments = []

        # Try to validate each segment
        for segment in segments:
            if segment == "..":
                if temp_path:
                    temp_path.pop()
                    valid_segments.append("..")
            elif segment != "." and segment:  # Skip "." and empty segments
                # Save the current path
                original_path = self._path.copy()

                # Temporarily set the path to the current temp_path
                self._path = temp_path.copy()

                try:
                    # Try to add the segment
                    self.add_segment(segment)
                    # If successful, add to valid segments and update temp_path
                    valid_segments.append(segment)
                    temp_path = self._path.copy()
                except Exception:
                    # If failed, restore the original path and break
                    self._path = original_path
                    raise Exception(f"Invalid segment {segment}")

        # Set the path to the temp_path (which contains all valid segments)
        self._path = temp_path
