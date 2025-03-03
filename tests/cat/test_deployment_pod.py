#!/usr/bin/env python3
"""
Test for the cat command on a specific pod of a deployment
"""
import os
import sys

from tests.common.test_framework import K8shTestFramework


def test_cat_deployment_pod(framework: K8shTestFramework) -> None:
    """Test the cat command on a specific pod of a deployment"""
    # Use absolute path to cat a specific pod of a deployment
    framework.run_test_commands([
        "cat /default/deployments/nginx-deployment/nginx-pod-1"
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


def test_cat_deployment_pod_with_long_name(framework: K8shTestFramework) -> None:
    """Test the cat command on a specific pod of a deployment with a complex name"""
    # Use a pod name with a complex format like in real Kubernetes
    framework.run_test_commands([
        "cat /default/deployments/nginx-deployment/nginx-deployment-7f5569bb7f-vsmbx"
    ])

    # We should still get the pod YAML even though the pod name is complex
    # In our mock implementation, this will fall back to a default pod
    framework.assert_output_contains([
        "apiVersion",
        "kind",
        "Pod",
        "metadata",
        "spec",
        "containers"
    ])
