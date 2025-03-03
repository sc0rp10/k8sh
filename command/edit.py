#!/usr/bin/env python3
"""
Edit command for K8sh
"""
import os
import subprocess
from typing import List, Optional

from command.base import FileCommand
from k8s_client import get_kubernetes_client
from state.state import State
from utils.terminal import Color, colorize

k8s_client = get_kubernetes_client()


class EditCommand(FileCommand):
    """Edit command for K8sh"""

    def get_name(self) -> str:
        """Get the name of the command"""
        return "edit"

    def get_help(self) -> str:
        """Get the help text for the command"""
        return "Edit a resource using kubectl edit"

    def get_aliases(self) -> List[str]:
        """Get the aliases for the command"""
        return ["vim", "nano"]

    def get_usage(self) -> str:
        """Get the extended usage information for the command"""
        edit_cmd = colorize("edit", Color.BRIGHT_YELLOW)
        vim_cmd = colorize("vim", Color.BRIGHT_YELLOW)
        nano_cmd = colorize("nano", Color.BRIGHT_YELLOW)
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
            f"{colorize('Usage:', Color.BRIGHT_GREEN)} {edit_cmd} {resource_path}",
            f"       {vim_cmd} {resource_path}  {colorize('# Use vim as editor', Color.BRIGHT_BLACK)}",
            f"       {nano_cmd} {resource_path}  {colorize('# Use nano as editor', Color.BRIGHT_BLACK)}",
            "",
            f"{colorize('Examples:', Color.BRIGHT_GREEN)}",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Edit a resource using the default editor (or EDITOR environment variable)",
            f"  {edit_cmd} {colorize_path('namespace/configmaps/my-config')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Edit a resource using vim",
            f"  {vim_cmd} {colorize_path('namespace/configmaps/my-config')}",
            "",
            f"  {colorize('#', Color.BRIGHT_BLACK)} Edit a resource using nano",
            f"  {nano_cmd} {colorize_path('namespace/configmaps/my-config')}",
            "",
            f"{colorize('Notes:', Color.BRIGHT_GREEN)}",
            f"  - The editor used depends on the command name or {colorize('EDITOR', Color.BRIGHT_MAGENTA)} environment variable",
            f"  - If using {colorize('edit', Color.BRIGHT_YELLOW)}, the {colorize('EDITOR', Color.BRIGHT_MAGENTA)} environment variable is used (defaults to {colorize('vi', Color.BRIGHT_YELLOW)})",
            f"  - If using {colorize('vim', Color.BRIGHT_YELLOW)} or {colorize('nano', Color.BRIGHT_YELLOW)}, that specific editor is used",
        ]
        return "\n".join(usage)

    def _get_filename(self, args: List[str]) -> Optional[str]:
        """Parse filename from args"""
        if not args:
            print("Error: No resource specified")
            return None

        return args[0]

    def _do_execute(self, state: State, namespace: str, resource_type: str, resource_name: str) -> None:
        """Execute the edit command"""
        # Handle special cases for directories
        if resource_type == "" and resource_name == "" and not namespace:
            # This is the root directory
            print(colorize("Error: Cannot use 'edit' on a directory. Use 'ls' to view directory contents.", Color.BRIGHT_RED))
            return

        # Prevent using edit on resource type directories
        if resource_type and not resource_name:
            print(colorize("Error: Cannot use 'edit' on a directory. Use 'ls' to view directory contents.", Color.BRIGHT_RED))
            return

        # Get the editor from environment variables or use vi as default
        name = state.get_current_command()

        if name in ["vim", "nano"]:
            editor = name
        else:
            editor = os.environ.get("EDITOR", "vi")

        # Determine the resource type and name based on the context
        if not resource_type:
            # If no resource type is specified, assume it's a namespace
            cmd = ["kubectl", "edit", "namespace", namespace]
        else:
            # For specific resource types with names
            cmd = ["kubectl", "edit", resource_type, resource_name, "-n", namespace]

        # In test mode (DEBUG=1), just print the command that would be run
        if os.environ.get("DEBUG") == "1":
            # Format the output exactly as the tests expect
            print(f"Would run: EDITOR={editor} {' '.join(cmd)}")
            return

        try:
            # Set the EDITOR environment variable for the subprocess
            env = os.environ.copy()
            env["EDITOR"] = editor

            # Execute the kubectl command
            subprocess.run(cmd, check=True, env=env)
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to edit resource: {e}")
        except FileNotFoundError:
            print("Error: kubectl command not found. Please ensure kubectl is installed and in your PATH.")
