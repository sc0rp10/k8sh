#!/usr/bin/env python3
"""
Test for the ls command with a path argument
"""


def test_ls_path_arg(framework):
    """Test the ls command with a path argument"""
    framework.run_test_commands(["ls default/services"])

    # Check if the output contains the path
    framework.assert_output_contains(["default/services"])
