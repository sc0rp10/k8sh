#!/usr/bin/env python3
"""
Test for the restart command on directories (should be prohibited)
"""
import os
import sys


def test_restart_directory_error(framework):
    """Test that using restart on a directory produces an error message"""
    # Try to restart a directory
    framework.run_test_commands([
        "restart /default/deployments"
    ])

    # Print the output for debugging if DEBUG=1 is set
    if os.environ.get("DEBUG") == "1" and framework.output:
        print("DEBUG OUTPUT:", file=sys.stderr)
        print(framework.output, file=sys.stderr)

    # Check if the output contains the error message
    framework.assert_output_contains([
        "Error: Cannot use 'restart' on a directory. Use 'ls' to view directory contents."
    ])


def test_restart_root_error(framework):
    """Test that using restart on the root directory produces an error message"""
    # Try to restart the root directory
    framework.run_test_commands([
        "restart /"
    ])

    # Check if the output contains the error message
    framework.assert_output_contains([
        "Error: Cannot use 'restart' on a directory. Use 'ls' to view directory contents."
    ])
