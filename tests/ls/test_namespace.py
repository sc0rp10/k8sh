#!/usr/bin/env python3
"""
Test for the ls command at namespace level
"""


def test_ls_namespace(framework):
    """Test the ls command at namespace level"""
    framework.run_test_commands(["cd default", "ls"])

    # Check if the output contains the expected resource types
    framework.assert_output_contains([
        "services", "deployments", "pods", "configmaps",
        "secrets", "replicasets", "daemonsets", "statefulsets"
    ])
