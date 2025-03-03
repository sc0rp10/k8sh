#!/usr/bin/env python3
"""
Test for the help command
"""


def test_help(framework):
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
