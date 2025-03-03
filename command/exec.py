#!/usr/bin/env python3
"""
Exec command for K8sh
"""
import os
import shlex
import subprocess
from typing import List, Tuple

from command.base import GenericCommand
from state.state import State
from utils.terminal import Color, colorize


class ExecCommand(GenericCommand):
    """Command to execute a shell in a Kubernetes resource"""

    def get_name(self) -> str:
        """Get the name of the command"""
        return "exec"

    def get_aliases(self) -> List[str]:
        """Get the aliases for the command"""
        return ["ssh"]

    def get_help(self) -> str:
        """Get the help text for the command"""
        return "Execute a shell in a Kubernetes resource (deployment, pod, or container)"

    def get_usage(self) -> str:
        """Get the extended usage information for the command"""
        cmd = colorize("exec", Color.BRIGHT_YELLOW)
        ssh_cmd = colorize("ssh", Color.BRIGHT_YELLOW)
        resource_path = colorize("<resource_path>", Color.BRIGHT_CYAN)
        command = colorize("[-- command]", Color.BRIGHT_MAGENTA)

        # Colorize resource paths in examples
        def colorize_path(path):
            parts = path.split('/')
            colored_parts = []
            for i, part in enumerate(parts):
                if i == 0:  # namespace
                    colored_parts.append(colorize(part, Color.BRIGHT_BLUE))
                elif i == 1:  # resource type
                    colored_parts.append(colorize(part, Color.BRIGHT_GREEN))
                else:  # resource name or container
                    colored_parts.append(colorize(part, Color.BRIGHT_CYAN))
            return '/'.join(colored_parts)

        usage = [
            f"{colorize('Usage:', Color.BRIGHT_GREEN)} {cmd} {resource_path} {command}",
            f"       {ssh_cmd} {resource_path} {command}",
            "",
            f"{colorize('Examples:', Color.BRIGHT_GREEN)}",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Execute bash in a deployment",
            f"  {cmd} {colorize_path('namespace/deployments/nginx-deployment')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Execute sh in a deployment",
            f"  {cmd} {colorize_path('namespace/deployments/nginx-deployment')} {colorize('-- sh', Color.BRIGHT_MAGENTA)}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Execute bash in a pod",
            f"  {cmd} {colorize_path('namespace/pods/nginx-pod-1234')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Execute bash in a pod within a deployment",
            f"  {cmd} {colorize_path('namespace/deployments/nginx-deployment/pods/nginx-pod-1234')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Execute bash in a specific container within a pod",
            f"  {cmd} {colorize_path('namespace/pods/nginx-pod-1234/nginx')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Execute sh in a specific container within a pod within a deployment",
            f"  {cmd} {colorize_path('namespace/deployments/nginx-deployment/pods/nginx-pod-1234/nginx')} {colorize('-- sh', Color.BRIGHT_MAGENTA)}",
        ]
        return "\n".join(usage)

    def _parse_args(self, args: List[str]) -> Tuple[List[str], List[str]]:
        """
        Parse the arguments to separate the resource path from the command to execute
        Returns a tuple of (resource_args, command_args)
        """
        if "--" in args:
            separator_index = args.index("--")
            resource_args = args[:separator_index]
            command_args = args[separator_index + 1:]
        else:
            resource_args = args
            command_args = ["bash"]  # Default to bash if no command specified

        return resource_args, command_args

    def execute(self, state: State, args: List[str]) -> None:
        """Execute the exec command"""
        if not args:
            print(colorize("Error: No resource specified", Color.BRIGHT_RED))
            print(f"{colorize('Usage:', Color.BRIGHT_GREEN)} {colorize('exec', Color.BRIGHT_YELLOW)} {colorize('<resource>', Color.BRIGHT_CYAN)} {colorize('[-- command]', Color.BRIGHT_MAGENTA)}")
            return

        resource_args, command_args = self._parse_args(args)
        resource_path = resource_args[0]

        # Parse the resource path
        if resource_path.startswith('/'):
            # Absolute path
            path_components = resource_path.strip('/').split('/')
        else:
            # Relative path - use current context
            current_path = state.get_current_path()
            if current_path == '/':
                # At root level
                path_components = [resource_path]
            else:
                # Combine current path with resource path
                combined_path = f"{current_path}/{resource_path}".strip('/')
                path_components = combined_path.split('/')

        # Determine the resource type and name based on the path
        if len(path_components) < 2:
            print(colorize(f"Error: Invalid resource path: {resource_path}", Color.BRIGHT_RED))
            return

        namespace = path_components[0]
        resource_type = path_components[1]

        if len(path_components) < 3:
            print(f"Error: No resource name specified in path: {resource_path}")
            return

        resource_name = '/'.join(path_components[2:])

        # Determine the resource type and construct the kubectl command
        if resource_type == "pods":
            # Direct pod execution
            kubectl_resource = resource_name
            container_option = ""

            # Check if we're targeting a specific container
            path_components = resource_name.split('/')
            if len(path_components) > 1:
                # Format: pods/pod-name/container-name
                pod_name = path_components[0]
                container_name = path_components[1]
                kubectl_resource = pod_name
                container_option = f"-c {container_name}"
        elif resource_type in ["deployments", "daemonsets", "statefulsets", "replicasets"]:
            # For workload controllers, we need to use the resource type/name format
            # Remove the 's' at the end of the resource type for kubectl
            kubectl_resource_type = resource_type[:-1]
            kubectl_resource = f"{kubectl_resource_type}/{resource_name}"
            container_option = ""

            # Check if we're targeting a specific pod
            path_components = resource_name.split('/')
            if len(path_components) > 1 and path_components[1] == "pods":
                # Format: deployment-name/pods/pod-name
                pod_name = path_components[2]
                kubectl_resource = pod_name
                container_option = ""

                # Check if we're targeting a specific container
                if len(path_components) > 3:
                    # Format: deployment-name/pods/pod-name/container-name
                    container_name = path_components[3]
                    container_option = f"-c {container_name}"
        else:
            print(f"Error: Cannot exec into resource type '{resource_type}'")
            return

        # Construct the kubectl command
        cmd_parts = ["kubectl", "exec", "-it"]

        # Add namespace if provided
        if namespace:
            cmd_parts.extend(["-n", namespace])

        # Add resource
        cmd_parts.append(kubectl_resource)

        # Add container option if specified
        if container_option:
            cmd_parts.extend(shlex.split(container_option))

        # Add command separator and command
        cmd_parts.append("--")
        cmd_parts.extend(command_args)

        # In test mode (K8SH_MOCK=1), just print the command that would be run
        if os.environ.get("K8SH_MOCK") == "1":
            print(f"Would run: {' '.join(cmd_parts)}")
            return

        try:
            # Execute the kubectl command
            subprocess.run(cmd_parts, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to exec into resource: {e}")
        except FileNotFoundError:
            print("Error: kubectl command not found")
