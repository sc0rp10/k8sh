#!/usr/bin/env python3
"""
Test for the ls command at root level
"""
from tests.common.test_framework import K8shTestFramework, run_test


def test_ls_root(framework: K8shTestFramework) -> None:
    """Test the ls command at root level"""
    framework.run_test_commands(["ls"])

    # Check if the output contains the expected namespaces
    framework.assert_output_contains(["default", "kube-system"])


if __name__ == "__main__":
    run_test(test_ls_root, "root", "ls", expected_items=["default", "kube-system"])
