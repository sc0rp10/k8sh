#!/usr/bin/env python3
"""
Pytest configuration for K8sh tests
"""
import os
import subprocess
import time
from typing import List, Generator

import pytest


class K8shTestFramework:
    """Test framework for K8sh tests"""

    def __init__(self):
        """Initialize the test framework"""
        self.env = os.environ.copy()
        self.env["K8SH_MOCK"] = "1"  # Always use mock mode for tests
        self.process = None
        self.output = ""

    def start_shell(self) -> subprocess.Popen:
        """Start the shell process"""
        self.process = subprocess.Popen(
            ["python3", "main.py", "--no-color"],  # Always disable colors in tests
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=self.env,
            universal_newlines=True,
            bufsize=1  # Line buffered
        )
        # Wait for the prompt to appear - reduced to 0.1s
        time.sleep(0.1)
        return self.process

    def send_command(self, command: str, wait_time: float = 0.1) -> None:
        """Send a command to the shell"""
        if self.process is None:
            raise RuntimeError("Shell process not started")

        if self.process.stdin is None:
            raise RuntimeError("Shell stdin is not available")

        self.process.stdin.write(f"{command}\n")
        self.process.stdin.flush()
        time.sleep(wait_time)  # Reduced to 0.1s

    def exit_shell(self) -> str:
        """Exit the shell and return the output"""
        if self.process is None:
            raise RuntimeError("Shell process not started")

        self.send_command("exit")
        stdout, _ = self.process.communicate(timeout=2)  # Reduced to 2s
        self.output = stdout
        self.process = None
        return self.output

    def run_test_commands(self, commands: List[str], wait_times: List[float] = None) -> str:
        """Run a list of commands and return the output"""
        if wait_times is None:
            wait_times = [0.1] * len(commands)  # Reduced to 0.1s
        elif len(wait_times) != len(commands):
            raise ValueError("Length of wait_times must match length of commands")

        self.start_shell()

        for command, wait_time in zip(commands, wait_times):
            self.send_command(command, wait_time)

        return self.exit_shell()

    def assert_output_contains(self, expected_items: List[str]) -> None:
        """Assert that the output contains all expected items"""
        for item in expected_items:
            assert item in self.output, f"Expected '{item}' in output, but it was not found"

    def assert_output_not_contains(self, unexpected_items: List[str]) -> None:
        """Assert that the output does not contain any unexpected items"""
        for item in unexpected_items:
            assert item not in self.output, f"Unexpected '{item}' found in output"


@pytest.fixture
def framework() -> Generator[K8shTestFramework, None, None]:
    """Fixture to provide a test framework"""
    framework = K8shTestFramework()
    yield framework
