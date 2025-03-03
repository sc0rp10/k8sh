#!/usr/bin/env python3
"""
Test for the cat command on a specific pod of a deployment using relative paths
"""
import os
import sys


def test_cat_deployment_pod_relative(framework):
    """Test the cat command on a specific pod of a deployment using relative paths"""
    # First cd to the deployment directory, then cat the pod using a relative path
    framework.run_test_commands([
        "cd /default/deployments/nginx-deployment",
        "cat nginx-pod-1"
    ])

    # Print the output for debugging if DEBUG=1 is set
    if os.environ.get("DEBUG") == "1" and framework.output:
        print("DEBUG OUTPUT:", file=sys.stderr)
        print(framework.output, file=sys.stderr)

    # Check if the output contains expected YAML elements for a pod
    framework.assert_output_contains([
        "apiVersion",
        "kind",
        "Pod",  # Should be Pod, not Deployment
        "metadata",
        "name",
        "nginx-pod-1",  # Should be the pod name
        "spec",
        "containers"
    ])

    # Check for the sidecar container that should be in the mock data
    framework.assert_output_contains([
        "sidecar",
        "nginx"
    ])
