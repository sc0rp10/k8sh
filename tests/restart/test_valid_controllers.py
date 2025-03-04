#!/usr/bin/env python3
"""
Test for the restart command on valid controllers
"""
import os
import sys


def test_restart_deployment(framework):
    """Test that using restart on a deployment works correctly"""
    # Try to restart a deployment
    framework.run_test_commands([
        "restart /default/deployments/nginx"
    ])

    # Print the output for debugging if DEBUG=1 is set
    if os.environ.get("DEBUG") == "1" and framework.output:
        print("DEBUG OUTPUT:", file=sys.stderr)
        print(framework.output, file=sys.stderr)

    # Check if the output contains the expected command
    framework.assert_output_contains([
        "Would run: kubectl rollout restart deployment nginx -n default"
    ])


def test_restart_statefulset(framework):
    """Test that using restart on a statefulset works correctly"""
    # Try to restart a statefulset
    framework.run_test_commands([
        "restart /default/statefulsets/web"
    ])

    # Check if the output contains the expected command
    framework.assert_output_contains([
        "Would run: kubectl rollout restart statefulset web -n default"
    ])


def test_restart_daemonset(framework):
    """Test that using restart on a daemonset works correctly"""
    # Try to restart a daemonset
    framework.run_test_commands([
        "restart /default/daemonsets/fluentd"
    ])

    # Check if the output contains the expected command
    framework.assert_output_contains([
        "Would run: kubectl rollout restart daemonset fluentd -n default"
    ])
