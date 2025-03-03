#!/usr/bin/env python3
"""
Test for the pwd command at root level
"""


def test_pwd_root(framework):
    """Test the pwd command at root level"""
    framework.run_test_commands(["pwd"])

    # Check if the output contains the root path
    framework.assert_output_contains(["$ pwd", ""])
