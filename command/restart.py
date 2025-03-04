#!/usr/bin/env python3
"""
Restart command for K8sh
"""
import os
import subprocess
from typing import List, Optional

from command.base import FileCommand
from k8s_client import get_kubernetes_client
from state.state import State
from utils.terminal import Color, colorize

k8s_client = get_kubernetes_client()


class RestartCommand(FileCommand):
    """Restart command for K8sh"""

    def get_name(self) -> str:
        """Get the name of the command"""
        return "restart"

    def get_help(self) -> str:
        """Get the help text for the command"""
        return "Restart a controller (deployment, statefulset, or daemonset)"

    def get_aliases(self) -> List[str]:
        """Get the aliases for the command"""
        return ["touch"]

    def get_usage(self) -> str:
        """Get the extended usage information for the command"""
        restart_cmd = colorize("restart", Color.BRIGHT_YELLOW)
        rollout_restart_cmd = colorize("rollout-restart", Color.BRIGHT_YELLOW)
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
            f"{colorize('Usage:', Color.BRIGHT_GREEN)} {restart_cmd} {resource_path}",
            f"       {rollout_restart_cmd} {resource_path}  {colorize('# Alternative command', Color.BRIGHT_BLACK)}",
            "",
            f"{colorize('Examples:', Color.BRIGHT_GREEN)}",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Restart a deployment",
            f"  {restart_cmd} {colorize_path('namespace/deployments/my-deployment')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Restart a statefulset",
            f"  {restart_cmd} {colorize_path('namespace/statefulsets/my-statefulset')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Restart a daemonset",
            f"  {restart_cmd} {colorize_path('namespace/daemonsets/my-daemonset')}",
            "",
            f"{colorize('Notes:', Color.BRIGHT_GREEN)}",
            "  - This command can only be used with deployments, statefulsets, and daemonsets",
            "  - It triggers a rolling restart of the pods managed by the controller",
            "  - The restart is performed by using 'kubectl rollout restart'",
        ]
        return "\n".join(usage)

    def _get_filename(self, args: List[str]) -> Optional[str]:
        """Parse filename from args"""
        if not args:
            print("Error: No resource specified")
            return None

        return args[0]

    def _do_execute(self, state: State, namespace: str, resource_type: str, resource_name: str) -> None:
        """Execute the restart command"""
        # Handle special cases for directories
        if resource_type == "" and resource_name == "" and not namespace:
            # This is the root directory
            print(colorize("Error: Cannot use 'restart' on a directory. Use 'ls' to view directory contents.", Color.BRIGHT_RED))
            return

        # Prevent using restart on resource type directories
        if resource_type and not resource_name:
            print(colorize("Error: Cannot use 'restart' on a directory. Use 'ls' to view directory contents.", Color.BRIGHT_RED))
            return

        # Check if the resource type is a controller
        valid_controllers = ["deployments", "statefulsets", "daemonsets"]
        if resource_type not in valid_controllers:
            print(colorize(f"Error: The 'restart' command can only be used with {', '.join(valid_controllers)}", Color.BRIGHT_RED))
            return

        # Convert plural resource type to singular for kubectl
        kubectl_resource_type = resource_type[:-1]  # Remove the 's' at the end

        # Prepare the kubectl command
        cmd = ["kubectl", "rollout", "restart", kubectl_resource_type, resource_name, "-n", namespace]

        # In test mode (DEBUG=1 or K8SH_MOCK=1), just print the command that would be run
        if os.environ.get("DEBUG") == "1" or os.environ.get("K8SH_MOCK") == "1":
            print(f"Would run: {' '.join(cmd)}")
            return

        try:
            # Execute the kubectl command
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to restart {resource_type}/{resource_name}: {e.stderr}")
        except FileNotFoundError:
            print("Error: kubectl command not found. Please ensure kubectl is installed and in your PATH.")
