#!/usr/bin/env python3
"""
Test for the cd command with a path argument
"""


def test_cd_path_arg(framework):
    """Test the cd command with a path argument"""
    framework.run_test_commands(["cd default/services", "pwd"])

    # Check if the output contains the expected path
    framework.assert_output_contains(["default/services"])
