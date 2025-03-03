#!/usr/bin/env python3
"""
Test for the cd command to a namespace
"""


def test_cd_namespace(framework):
    """Test the cd command to a namespace"""
    framework.run_test_commands(["cd default", "pwd"])

    # Check if the output contains the expected path
    framework.assert_output_contains(["default"])
