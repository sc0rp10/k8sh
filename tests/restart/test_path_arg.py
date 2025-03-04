#!/usr/bin/env python3
"""
Test for the restart command with different path arguments
"""
import os
import sys


def test_restart_no_args(framework):
    """Test that using restart without arguments produces an error message"""
    # Try to restart without arguments
    framework.run_test_commands([
        "restart"
    ])

    # Print the output for debugging if DEBUG=1 is set
    if os.environ.get("DEBUG") == "1" and framework.output:
        print("DEBUG OUTPUT:", file=sys.stderr)
        print(framework.output, file=sys.stderr)

    # Check if the output contains the error message
    framework.assert_output_contains([
        "Error: No resource specified"
    ])


def test_restart_relative_path(framework):
    """Test that using restart with a relative path works correctly"""
    # Set up the environment by changing to a namespace and then a resource type
    framework.run_test_commands([
        "cd /default/deployments",
        "restart nginx"
    ])

    # Check if the output contains the expected command
    framework.assert_output_contains([
        "Would run: kubectl rollout restart deployment nginx -n default"
    ])


def test_restart_with_alias(framework):
    """Test that using the restart alias works correctly"""
    # Try to restart a deployment using the alias
    framework.run_test_commands([
        "rollout-restart /default/deployments/nginx"
    ])

    # Check if the output contains the expected command
    framework.assert_output_contains([
        "Would run: kubectl rollout restart deployment nginx -n default"
    ])
