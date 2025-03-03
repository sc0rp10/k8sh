#!/usr/bin/env python3
"""
Test for the ls command at root level
"""


def test_ls_root(framework):
    """Test the ls command at root level"""
    framework.run_test_commands(["ls"])

    # Check if the output contains the expected namespaces
    framework.assert_output_contains(["default", "kube-system"])
