#!/usr/bin/env python3
"""
Test for the edit command on directories (should be prohibited)
"""
import os
import sys


def test_edit_directory_error(framework):
    """Test that using edit on a directory produces an error message"""
    # Try to edit a directory
    framework.run_test_commands([
        "edit /default/deployments"
    ])

    # Print the output for debugging if DEBUG=1 is set
    if os.environ.get("DEBUG") == "1" and framework.output:
        print("DEBUG OUTPUT:", file=sys.stderr)
        print(framework.output, file=sys.stderr)

    # Check if the output contains the error message
    framework.assert_output_contains([
        "Error: Cannot use 'edit' on a directory. Use 'ls' to view directory contents."
    ])


def test_edit_root_error(framework):
    """Test that using edit on the root directory produces an error message"""
    # Try to edit the root directory
    framework.run_test_commands([
        "edit /"
    ])

    # Check if the output contains the error message
    framework.assert_output_contains([
        "Error: Cannot use 'edit' on a directory. Use 'ls' to view directory contents."
    ])


def test_vim_directory_error(framework):
    """Test that using vim on a directory produces an error message"""
    # Try to vim a directory
    framework.run_test_commands([
        "vim /default/deployments"
    ])

    # Check if the output contains the error message
    framework.assert_output_contains([
        "Error: Cannot use 'edit' on a directory. Use 'ls' to view directory contents."
    ])
