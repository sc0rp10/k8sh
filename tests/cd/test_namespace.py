#!/usr/bin/env python3
"""
Test for the cd command to a namespace
"""
from tests.common.test_framework import K8shTestFramework, run_test


def test_cd_namespace(framework: K8shTestFramework) -> None:
    """Test the cd command to a namespace"""
    framework.run_test_commands(["cd default", "pwd"])

    # Check if the output contains the expected path
    framework.assert_output_contains(["default"])


if __name__ == "__main__":
    run_test(test_cd_namespace, "namespace", "cd", expected_items=["/default"])
