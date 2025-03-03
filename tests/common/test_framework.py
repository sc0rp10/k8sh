#!/usr/bin/env python3
"""
Common test framework for K8sh tests
"""
import os
import subprocess
import time
from typing import List, Optional, Callable


class K8shTestFramework:
    """Common test framework for K8sh tests"""

    def __init__(self, use_mock: bool = True):
        """Initialize the test framework"""
        self.env = os.environ.copy()
        if use_mock:
            self.env["K8SH_MOCK"] = "1"
        # Set DEBUG to 1 to see the output
        self.env["DEBUG"] = "1"
        self.process: Optional[subprocess.Popen] = None
        self.output: Optional[str] = None

    def start_shell(self) -> subprocess.Popen:
        """Start the shell process"""
        # Start the shell process
        self.process = subprocess.Popen(
            ["python3", "main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=self.env,
            universal_newlines=True,
            bufsize=1  # Line buffered
        )

        # Wait for the prompt to appear - reduced from 0.5 to 0.1
        time.sleep(0.1)

        if self.process is None:
            raise RuntimeError("Failed to start shell process")

        return self.process

    def send_command(self, command: str, wait_time: float = 0.1) -> None:
        """Send a command to the shell"""
        if self.process is None:
            raise RuntimeError("Shell process not started")

        if self.process.stdin is None:
            raise RuntimeError("Shell stdin is not available")

        # Send the command
        self.process.stdin.write(f"{command}\n")
        self.process.stdin.flush()

        # Wait for the command to execute - reduced from 0.5 to 0.1
        time.sleep(wait_time)

    def exit_shell(self) -> str:
        """Exit the shell and return the output"""
        if self.process is None:
            raise RuntimeError("Shell process not started")

        # Send exit command
        self.send_command("exit")

        # Wait for the process to exit
        stdout, _ = self.process.communicate(timeout=2)  # Reduced from 5 to 2
        self.output = stdout
        self.process = None

        if self.output is None:
            raise RuntimeError("Failed to get output")

        return self.output

    def run_test_commands(self, commands: List[str], wait_times: Optional[List[float]] = None) -> str:
        """Run a list of commands and return the output"""
        if wait_times is None:
            wait_times = [0.1] * len(commands)  # Reduced from 0.5 to 0.1
        elif len(wait_times) != len(commands):
            raise ValueError("Length of wait_times must match length of commands")

        self.start_shell()

        for command, wait_time in zip(commands, wait_times):
            self.send_command(command, wait_time)

        return self.exit_shell()

    def assert_output_contains(self, expected_items: List[str]) -> None:
        """Assert that the output contains all expected items"""
        if self.output is None:
            raise RuntimeError("No output available")

        for item in expected_items:
            assert item in self.output, f"Expected '{item}' in output, but it was not found"

    def assert_output_not_contains(self, unexpected_items: List[str]) -> None:
        """Assert that the output does not contain any unexpected items"""
        if self.output is None:
            raise RuntimeError("No output available")

        for item in unexpected_items:
            assert item not in self.output, f"Unexpected '{item}' found in output"

    def assert_output_contains_pattern(self, pattern: str) -> None:
        """Assert that the output contains a pattern (using regex)"""
        if self.output is None:
            raise RuntimeError("No output available")

        import re
        assert re.search(pattern, self.output, re.MULTILINE) is not None, f"Pattern '{pattern}' not found in output"


def run_test(
        test_func: Callable[[K8shTestFramework], None],
        test_name: str,
        command_dir: str,
        expected_items: Optional[List[str]] = None,
        unexpected_items: Optional[List[str]] = None,
        expected_pattern: Optional[str] = None
) -> None:
    """Run a test function and perform assertions"""
    framework = K8shTestFramework()
    test_func(framework)

    if expected_items:
        framework.assert_output_contains(expected_items)

    if unexpected_items:
        framework.assert_output_not_contains(unexpected_items)

    if expected_pattern:
        framework.assert_output_contains_pattern(expected_pattern)

    # Always print success message
    print(f"Test {test_name} passed")
