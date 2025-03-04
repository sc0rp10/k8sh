#!/usr/bin/env python3
"""
Test for the restart command on invalid resource types
"""
import os
import sys


def test_restart_invalid_resource_type(framework):
    """Test that using restart on an invalid resource type produces an error message"""
    # Try to restart a resource type that is not a controller
    framework.run_test_commands([
        "restart /default/pods/nginx"
    ])

    # Print the output for debugging if DEBUG=1 is set
    if os.environ.get("DEBUG") == "1" and framework.output:
        print("DEBUG OUTPUT:", file=sys.stderr)
        print(framework.output, file=sys.stderr)

    # Check if the output contains the error message
    framework.assert_output_contains([
        "Error: The 'restart' command can only be used with deployments, statefulsets, daemonsets"
    ])


def test_restart_configmap_error(framework):
    """Test that using restart on a configmap produces an error message"""
    # Try to restart a configmap
    framework.run_test_commands([
        "restart /default/configmaps/my-config"
    ])

    # Check if the output contains the error message
    framework.assert_output_contains([
        "Error: The 'restart' command can only be used with deployments, statefulsets, daemonsets"
    ])


def test_restart_service_error(framework):
    """Test that using restart on a service produces an error message"""
    # Try to restart a service
    framework.run_test_commands([
        "restart /default/services/my-service"
    ])

    # Check if the output contains the error message
    framework.assert_output_contains([
        "Error: The 'restart' command can only be used with deployments, statefulsets, daemonsets"
    ])
