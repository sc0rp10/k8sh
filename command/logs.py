#!/usr/bin/env python3
"""
Logs command for K8sh
"""
import os
import shlex
import subprocess
import json
from typing import List, Tuple, Optional

from command.base import GenericCommand
from state.state import State
from utils.terminal import Color, colorize


class LogsCommand(GenericCommand):
    """Command to display logs from a Kubernetes resource"""

    def get_name(self) -> str:
        """Get the name of the command"""
        return "logs"

    def get_aliases(self) -> List[str]:
        """Get the aliases for the command"""
        return ["tail"]

    def get_help(self) -> str:
        """Get the help text for the command"""
        return "Display logs from a Kubernetes resource (deployment, pod, or container)"

    def get_usage(self) -> str:
        """Get the extended usage information for the command"""
        cmd = colorize("logs", Color.BRIGHT_YELLOW)
        tail_cmd = colorize("tail", Color.BRIGHT_YELLOW)
        resource_path = colorize("<resource_path>", Color.BRIGHT_CYAN)
        follow_flag = colorize("[-f]", Color.BRIGHT_MAGENTA)
        tail_flag = colorize("[-n <lines>]", Color.BRIGHT_MAGENTA)

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
            f"{colorize('Usage:', Color.BRIGHT_GREEN)} {cmd} {follow_flag} {tail_flag} {resource_path}",
            f"       {tail_cmd} {follow_flag} {tail_flag} {resource_path}",
            "",
            f"{colorize('Examples:', Color.BRIGHT_GREEN)}",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Display logs from a pod",
            f"  {cmd} {colorize_path('namespace/pods/nginx-pod-1234')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Display logs from a specific container in a pod",
            f"  {cmd} {colorize_path('namespace/pods/nginx-pod-1234/nginx')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Display logs from a deployment",
            f"  {cmd} {colorize_path('namespace/deployments/nginx-deployment')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Automatically select a pod from a deployment's pods",
            f"  {cmd} {colorize_path('namespace/deployments/nginx-deployment/pods/')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Follow logs in real-time",
            f"  {cmd} {colorize('-f', Color.BRIGHT_MAGENTA)} {colorize_path('namespace/pods/nginx-pod-1234')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Show only the last 10 lines",
            f"  {cmd} {colorize('-n 10', Color.BRIGHT_MAGENTA)} {colorize_path('namespace/pods/nginx-pod-1234')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Follow logs and show only the last 50 lines",
            f"  {cmd} {colorize('-f -n 50', Color.BRIGHT_MAGENTA)} {colorize_path('namespace/pods/nginx-pod-1234')}",
            "",
            f"{colorize('Notes:', Color.BRIGHT_GREEN)}",
            "  - The resource must be a pod, deployment, statefulset, daemonset, or replicaset",
            f"  - Use {colorize('-f', Color.BRIGHT_MAGENTA)} to follow logs in real-time (like {colorize('tail -f', Color.BRIGHT_YELLOW)})",
            f"  - Use {colorize('-n <lines>', Color.BRIGHT_MAGENTA)} to specify the number of lines to show (default: 100)",
            "  - For deployments and other controllers, logs from the first pod are shown",
            "  - You can use a path ending with /pods/ to automatically select a pod from a deployment",
        ]
        return "\n".join(usage)

    def _try_auto_select_pod(self, resource_path: str) -> Optional[Tuple[str, str]]:
        """
        Try to automatically select a pod for a deployment when path ends with /pods/
        Returns tuple of (pod_name, namespace) if successful, None otherwise
        """
        # Check if the path ends with /pods/ or pods/
        # Make sure it's really at the end by checking no additional path elements after pods/
        # This prevents matching paths like 'example-deployment/pods/something/else'
        if not (resource_path.endswith('/pods/') or resource_path.endswith('pods/')):
            return None

        # If there are additional segments after 'pods/' in the path, don't auto-select
        # Split the path to find the pods directory
        path_parts = resource_path.split('/')
        pods_index = -1

        # Find the index of 'pods' in the path
        for i, part in enumerate(path_parts):
            if part == 'pods':
                pods_index = i

        # If 'pods' is not the last non-empty segment, don't auto-select
        if pods_index != len(path_parts) - 2:  # -2 because the last element is '' due to trailing slash
            return None

        # Extract the deployment name from path
        deployment_name = resource_path.rstrip('/pods/').rstrip('/')
        if '/' in deployment_name:
            # If there's a namespace specified, extract it
            parts = deployment_name.split('/')
            if len(parts) >= 2:
                namespace = parts[0]
                deployment_name = parts[-1]  # Take the last part as deployment name
            else:
                namespace = "default"
        else:
            namespace = "default"

        # In test/mock mode, just return a fake pod
        if os.environ.get("DEBUG") == "1" or os.environ.get("K8SH_MOCK") == "1":
            fake_pod_name = f"{deployment_name}-7f5569bb7f-vsmbx"
            print(f"Found 3 pods, using pod/{fake_pod_name}")
            return fake_pod_name, namespace

        # Get pods for this deployment using kubectl
        try:
            # Build a kubectl command to get pods for this deployment
            cmd = f"kubectl get pods -n {namespace} -l app={deployment_name} -o json"
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True, check=True)
            pod_list = json.loads(result.stdout)

            # Check if we got any pods
            if pod_list.get('items'):
                pods = pod_list['items']
                pod_count = len(pods)

                if pod_count > 0:
                    # Get the first pod's name
                    pod_name = pods[0]['metadata']['name']
                    print(f"Found {pod_count} pods, using pod/{pod_name}")
                    return pod_name, namespace

            # If we get here, no pods were found
            print(f"No pods found for deployment {deployment_name}")
            return None

        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            print(f"Error getting pods for deployment {deployment_name}: {e}")
            return None

    def _parse_args(self, args: List[str]) -> Tuple[List[str], bool, int]:
        """
        Parse the arguments to extract flags and resource path
        Returns a tuple of (resource_args, follow, tail_lines)
        """
        resource_args = []
        follow = False
        tail_lines = 100  # Default to 100 lines

        i = 0
        while i < len(args):
            if args[i] == "-f":
                follow = True
                i += 1
            elif args[i] == "-n":
                if i + 1 < len(args):
                    try:
                        tail_lines = int(args[i + 1])
                        i += 2
                    except ValueError:
                        print(colorize(f"Error: Invalid number of lines: {args[i + 1]}", Color.BRIGHT_RED))
                        i += 2
                else:
                    print(colorize("Error: -n flag requires a number", Color.BRIGHT_RED))
                    i += 1
            else:
                resource_args.append(args[i])
                i += 1

        return resource_args, follow, tail_lines

    def execute(self, state: State, args: List[str]) -> None:
        """Execute the logs command"""
        if not args:
            print(colorize("Error: No resource specified", Color.BRIGHT_RED))
            print(f"{colorize('Usage:', Color.BRIGHT_GREEN)} {colorize('logs', Color.BRIGHT_YELLOW)} {colorize('[-f] [-n <lines>]', Color.BRIGHT_MAGENTA)} {colorize('<resource>', Color.BRIGHT_CYAN)}")
            return

        resource_args, follow, tail_lines = self._parse_args(args)

        if not resource_args:
            print(colorize("Error: No resource specified", Color.BRIGHT_RED))
            return

        resource_path = resource_args[0]

        # Handle automatic pod selection for paths ending with /pods/
        pods = self._try_auto_select_pod(resource_path)
        if pods:
            # We found pods for this deployment, use the first one
            pod_name, namespace = pods
            kubectl_cmd = "kubectl logs"
            follow_flag = "-f" if follow else ""
            tail_flag = f"--tail {tail_lines}"

            cmd = f"{kubectl_cmd} {follow_flag} {tail_flag} -n {namespace} {pod_name}".strip()

            if os.environ.get("DEBUG") == "1" or os.environ.get("K8SH_MOCK") == "1":
                print(f"Would run: {cmd}")
                return
            else:
                # Run the actual command
                subprocess.run(cmd, shell=True)
                return

        # Special case for pod names: if in a controller directory and arg looks like a pod
        # (has multiple hyphens and contains controller name), use it directly
        current_path = state.get_current_path()

        # Check if the current path is a controller path
        controller_path_parts = current_path.split('/')

        if len(controller_path_parts) >= 3 and controller_path_parts[1] in [
            "deployments", "daemonsets", "statefulsets", "replicasets"
        ]:
            controller_name = controller_path_parts[2]  # e.g., 'example-deployment'

            # Check if the resource path might be a pod name (contains controller name + random hash)
            container_part = ""
            pod_part = resource_path

            # Check if there's a slash (pod/container format)
            if '/' in resource_path:
                parts = resource_path.split('/', 1)
                pod_part = parts[0]
                container_part = parts[1] if len(parts) > 1 else ""

            # Use pod name detection heuristic:
            # 1. Contains controller name
            # 2. Has at least 2 hyphens (controller-hash-hash pattern)
            # 3. Not starting with a path structure like 'pods/' etc.
            if controller_name in pod_part and pod_part.count('-') >= 2 and '/' not in pod_part:
                namespace = controller_path_parts[0]
                kubectl_cmd = "kubectl logs"
                follow_flag = "-f" if follow else ""
                tail_flag = f"--tail {tail_lines}"
                container_flag = f"-c {container_part}" if container_part else ""

                cmd = f"{kubectl_cmd} {follow_flag} {tail_flag} -n {namespace} {pod_part} {container_flag}".strip()

                if os.environ.get("DEBUG") == "1" or os.environ.get("K8SH_MOCK") == "1":
                    print(f"Would run: {cmd}")
                    return
                else:
                    # Run the actual command
                    subprocess.run(cmd, shell=True)
                    return

        # Regular processing for standard paths
        # Parse the resource path
        if resource_path.startswith('/'):
            # Absolute path
            path_components = resource_path.strip('/').split('/')
        else:
            # Relative path - use current context
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
            print(colorize(f"Error: No resource name specified in path: {resource_path}", Color.BRIGHT_RED))
            return

        resource_name = '/'.join(path_components[2:])

        # Determine the resource type and construct the kubectl command
        if resource_type == "pods":
            # Direct pod logs
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
            # Extract parts from the path if it contains a pod or container name
            path_components = resource_name.split('/')
            controller_name = path_components[0]  # First part (e.g., 'example-deployment')

            # Check for arguments that look like pod names (with pod ID hash)
            # Pod names in k8s typically follow pattern: deployment-name-randomhash-randomhash
            # They'll have multiple hyphens and often end with an alphanumeric hash
            arg = resource_name
            container_name = ""

            # Split into parts if there's a slash (might be pod/container format)
            if '/' in arg:
                parts = arg.split('/')
                arg = parts[0]  # The pod/resource name
                if len(parts) > 1:
                    container_name = parts[1]  # The container name

            # Check if this is a pod name (pods have hyphen-randomhash pattern)
            # Typical pattern is controller-name-random-random
            if controller_name in arg and arg != controller_name and '-' in arg:
                parts = arg.split('-')
                if len(parts) >= 3:  # At least 3 parts with hyphen separators likely means it's a pod
                    kubectl_resource = arg  # Use the full argument as the pod name
                    container_option = f"-c {container_name}" if container_name else ""
                else:
                    # Not a pod name - use controller resource syntax
                    kubectl_resource_type = resource_type[:-1]  # Remove 's' at the end
                    kubectl_resource = f"{kubectl_resource_type}/{controller_name}"
                    container_option = ""
            else:
                # Standard approach - use resource type with controller name
                kubectl_resource_type = resource_type[:-1]  # Remove 's' at the end
                kubectl_resource = f"{kubectl_resource_type}/{controller_name}"
                container_option = ""
        else:
            print(colorize(f"Error: Cannot get logs from resource type '{resource_type}'", Color.BRIGHT_RED))
            print(colorize("Supported resource types: pods, deployments, daemonsets, statefulsets, replicasets", Color.BRIGHT_YELLOW))
            return

        # Construct the kubectl command
        cmd_parts = ["kubectl", "logs"]

        # Add follow flag if specified
        if follow:
            cmd_parts.append("-f")

        # Add tail lines
        cmd_parts.extend(["--tail", str(tail_lines)])

        # Add namespace if provided
        if namespace:
            cmd_parts.extend(["-n", namespace])

        # Add resource
        cmd_parts.append(kubectl_resource)

        # Add container option if specified
        if container_option:
            cmd_parts.extend(shlex.split(container_option))

        # In test mode (DEBUG=1 or K8SH_MOCK=1), just print the command that would be run
        if os.environ.get("DEBUG") == "1" or os.environ.get("K8SH_MOCK") == "1":
            print(f"Would run: {' '.join(cmd_parts)}")
            return

        try:
            # Execute the kubectl command
            subprocess.run(cmd_parts, check=True)
        except subprocess.CalledProcessError as e:
            print(colorize(f"Error: Failed to get logs from resource: {e}", Color.BRIGHT_RED))
        except FileNotFoundError:
            print(colorize("Error: kubectl command not found", Color.BRIGHT_RED))
