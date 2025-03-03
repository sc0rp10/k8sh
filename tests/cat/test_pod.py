#!/usr/bin/env python3
"""
Test for the cat command on a pod resource
"""
import os
import sys


def test_cat_pod(framework):
    """Test the cat command on a pod resource"""
    # Use absolute path to cat a pod
    framework.run_test_commands([
        "cat /default/pods/nginx-pod-1"
    ])

    # Print the output for debugging if DEBUG=1 is set
    if os.environ.get("DEBUG") == "1" and framework.output:
        print("DEBUG OUTPUT:", file=sys.stderr)
        print(framework.output, file=sys.stderr)

    # Check if the output contains expected YAML elements
    framework.assert_output_contains([
        "apiVersion",
        "kind",
        "Pod",
        "metadata",
        "name",
        "nginx-pod-1",
        "spec",
        "containers"
    ])

    # Check for the sidecar container that should be in the mock data
    framework.assert_output_contains([
        "sidecar",
        "busybox"
    ])
