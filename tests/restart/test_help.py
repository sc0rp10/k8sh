#!/usr/bin/env python3
"""
Test for the help command with restart
"""
import os
import sys


def test_help_restart(framework):
    """Test that the help command for restart shows the correct information"""
    # Run the help command for restart
    framework.run_test_commands([
        "help restart"
    ])

    # Print the output for debugging if DEBUG=1 is set
    if os.environ.get("DEBUG") == "1" and framework.output:
        print("DEBUG OUTPUT:", file=sys.stderr)
        print(framework.output, file=sys.stderr)

    # Check if the output contains the expected help text
    framework.assert_output_contains([
        "restart",
        "Restart a controller (deployment, statefulset, or daemonset)",
        "Usage:",
        "Examples:",
        "Restart a deployment",
        "Restart a statefulset",
        "Restart a daemonset",
        "Notes:",
        "This command can only be used with deployments, statefulsets, and daemonsets",
        "It triggers a rolling restart of the pods managed by the controller",
        "The restart is performed by using 'kubectl rollout restart'"
    ])
