#!/usr/bin/env python3
"""
Test for the pwd command after changing directory
"""


def test_pwd_after_cd(framework):
    """Test the pwd command after changing directory"""
    framework.run_test_commands(["cd default/services", "pwd"])

    # Check if the output contains the expected path
    framework.assert_output_contains(["default/services"])
