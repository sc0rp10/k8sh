#!/usr/bin/env python3
"""
Test for the exit command
"""


def test_exit(framework):
    """Test the exit command"""
    framework.run_test_commands(["exit"])  # Explicitly run exit command

    # Check if the output contains the exit message
    framework.assert_output_contains(["Exiting shell"])
