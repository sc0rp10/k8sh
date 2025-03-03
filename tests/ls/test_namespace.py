#!/usr/bin/env python3
"""
Test for the ls command at namespace level
"""
from tests.common.test_framework import K8shTestFramework, run_test


def test_ls_namespace(framework: K8shTestFramework) -> None:
    """Test the ls command at namespace level"""
    framework.run_test_commands(["cd default", "ls"])

    # Check if the output contains the expected resource types
    framework.assert_output_contains([
        "services", "deployments", "pods", "configmaps",
        "secrets", "replicasets", "daemonsets", "statefulsets"
    ])


if __name__ == "__main__":
    run_test(
        test_ls_namespace,
        "namespace",
        "ls",
        expected_items=[
            "services", "deployments", "pods", "configmaps",
            "secrets", "replicasets", "daemonsets", "statefulsets"
        ]
    )
