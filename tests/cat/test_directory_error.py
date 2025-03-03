#!/usr/bin/env python3
"""
Test for the cat command on directories (should be prohibited)
"""
import os
import sys

from tests.common.test_framework import K8shTestFramework


def test_cat_directory_error(framework: K8shTestFramework) -> None:
    """Test that using cat on a directory produces an error message"""
    # Try to cat a directory
    framework.run_test_commands([
        "cat /default/deployments"
    ])

    # Print the output for debugging if DEBUG=1 is set
    if os.environ.get("DEBUG") == "1" and framework.output:
        print("DEBUG OUTPUT:", file=sys.stderr)
        print(framework.output, file=sys.stderr)

    # Check if the output contains the error message
    framework.assert_output_contains([
        "Error: Cannot use 'cat' on a directory. Use 'ls' to view directory contents."
    ])


def test_cat_namespace_success(framework: K8shTestFramework) -> None:
    """Test that using cat on a namespace works correctly"""
    # Try to cat a namespace - this should work as namespaces are resources
    framework.run_test_commands([
        "cat /default"
    ])

    # Check if the output contains the namespace YAML
    framework.assert_output_contains([
        "apiVersion",
        "kind",
        "Namespace",
        "metadata",
        "name",
        "default"
    ])


def test_cat_resource_type_error(framework: K8shTestFramework) -> None:
    """Test that using cat on a resource type produces an error message"""
    # Try to cat a resource type
    framework.run_test_commands([
        "cd /default",
        "cat deployments"
    ])

    # Check if the output contains the error message
    # The current implementation returns a different error message
    framework.assert_output_contains([
        "Cannot use 'cat' on a directory. Use 'ls' to view directory contents."
    ])
