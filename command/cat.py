from typing import List, Optional

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import YamlLexer
from utils.terminal import Color, colorize

from command.base import FileCommand
from k8s_client import get_kubernetes_client
from state.state import State

k8s_client = get_kubernetes_client()


class CatCommand(FileCommand):
    """Command to display the YAML definition of a resource"""

    def get_name(self) -> str:
        """Get the name of the command"""
        return "cat"

    def get_aliases(self) -> List[str]:
        """Get the aliases for the command"""
        return ["view", "show"]

    def get_help(self) -> str:
        """Get the help text for the command"""
        return "Display the YAML definition of a resource"

    def get_usage(self) -> str:
        """Get the extended usage information for the command"""
        cmd = colorize("cat", Color.BRIGHT_YELLOW)
        view_cmd = colorize("view", Color.BRIGHT_YELLOW)
        show_cmd = colorize("show", Color.BRIGHT_YELLOW)
        resource_path = colorize("<resource_path>", Color.BRIGHT_CYAN)

        # Colorize resource paths in examples
        def colorize_path(path):
            parts = path.split('/')
            colored_parts = []
            for i, part in enumerate(parts):
                if i == 0:  # namespace
                    colored_parts.append(colorize(part, Color.BRIGHT_BLUE))
                elif i == 1:  # resource type
                    colored_parts.append(colorize(part, Color.BRIGHT_GREEN))
                else:  # resource name
                    colored_parts.append(colorize(part, Color.BRIGHT_CYAN))
            return '/'.join(colored_parts)

        usage = [
            f"{colorize('Usage:', Color.BRIGHT_GREEN)} {cmd} {resource_path}",
            f"       {view_cmd} {resource_path}",
            f"       {show_cmd} {resource_path}",
            "",
            f"{colorize('Examples:', Color.BRIGHT_GREEN)}",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Display the YAML definition of a service",
            f"  {cmd} {colorize_path('default/services/kubernetes')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Display the YAML definition of a pod",
            f"  {cmd} {colorize_path('default/pods/nginx-pod-1234')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Display the YAML definition of a configmap",
            f"  {cmd} {colorize_path('default/configmaps/my-config')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Display the YAML definition of a specific pod in a deployment",
            f"  {cmd} {colorize_path('default/deployments/example-deployment/example-deployment-7f5569bb7f-vsmbx')}",
            "",
            f"{colorize('Notes:', Color.BRIGHT_GREEN)}",
            f"  - The resource must be a {colorize('file', Color.BRIGHT_CYAN)}, not a {colorize('directory', Color.BRIGHT_BLUE)}",
            f"  - Supports both {colorize('absolute paths', Color.BRIGHT_CYAN)} (starting with /) and {colorize('relative paths', Color.BRIGHT_CYAN)}",
            f"  - The output is {colorize('syntax-highlighted YAML', Color.BRIGHT_MAGENTA)}",
            f"  - You can access specific pods of a deployment using the path format: {colorize('/namespace/deployments/deployment-name/pod-name', Color.BRIGHT_CYAN)}",
        ]
        return "\n".join(usage)

    def _get_filename(self, args: List[str]) -> Optional[str]:
        """Parse filename from args"""
        if not args:
            print(colorize("Error: No filename provided", Color.BRIGHT_RED))
            return None

        return args[0]

    def _do_execute(self, state: State, namespace: str, resource_type: str, resource_name: str) -> None:
        """Execute the cat command"""
        # Handle special cases for directories
        if resource_type == "" and resource_name == "":
            # This is a namespace
            if namespace:
                # We can cat a namespace as it's a resource
                yaml_content = k8s_client.get_resource_yaml("", "namespaces", namespace)
                if yaml_content:
                    highlighted_yaml = highlight(yaml_content, YamlLexer(), TerminalFormatter())
                    print(highlighted_yaml)
                    return
            else:
                # This is the root directory
                print(colorize("Error: Cannot use 'cat' on a directory. Use 'ls' to view directory contents.", Color.BRIGHT_RED))
                return

        # Prevent using cat on resource type directories
        if resource_type and not resource_name:
            print(colorize("Error: Cannot use 'cat' on a directory. Use 'ls' to view directory contents.", Color.BRIGHT_RED))
            return

        # Check if we're trying to access a pod that belongs to a deployment
        # Path format would be: /namespace/deployments/deployment-name/pod-name

        # Handle the case where we're trying to cat a specific pod of a deployment
        if (resource_type in ["deployments", "statefulsets", "daemonsets", "replicasets"] and resource_name and '/' in resource_name):
            # Split the resource name to get the deployment name and pod name
            parts = resource_name.split('/')
            if len(parts) == 2:
                pod_name = parts[1]
                # Now we want to cat the pod, not the deployment
                yaml_content = k8s_client.get_resource_yaml(namespace, "pods", pod_name)

                if yaml_content:
                    # Apply syntax highlighting
                    highlighted_yaml = highlight(yaml_content, YamlLexer(), TerminalFormatter())
                    print(highlighted_yaml)
                else:
                    print(colorize(f"Error: Could not get YAML definition for pod {pod_name}", Color.BRIGHT_RED))
                return

        # Regular case - get the YAML definition of the resource
        yaml_content = k8s_client.get_resource_yaml(namespace, resource_type, resource_name)

        if yaml_content:
            # Apply syntax highlighting
            highlighted_yaml = highlight(yaml_content, YamlLexer(), TerminalFormatter())
            print(highlighted_yaml)
        else:
            print(colorize(f"Error: Could not get YAML definition for {resource_type}/{resource_name}", Color.BRIGHT_RED))
