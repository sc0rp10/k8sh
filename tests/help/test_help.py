#!/usr/bin/env python3
"""
Test for the help command
"""
from tests.common.test_framework import K8shTestFramework, run_test


def test_help(framework: K8shTestFramework) -> None:
    """Test the help command"""
    framework.run_test_commands(["help"])

    # Check if the output contains the expected help information
    framework.assert_output_contains([
        "Available commands",
        "ls",
        "cd",
        "pwd",
        "help",
        "exit"
    ])


if __name__ == "__main__":
    run_test(
        test_help,
        "help",
        "help",
        expected_items=["Available commands", "ls", "cd", "pwd", "help", "exit"]
    )
