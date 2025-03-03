#!/usr/bin/env python3
"""
Test for the pwd command after changing directory
"""
from tests.common.test_framework import K8shTestFramework, run_test


def test_pwd_after_cd(framework: K8shTestFramework) -> None:
    """Test the pwd command after changing directory"""
    framework.run_test_commands(["cd default/services", "pwd"])

    # Check if the output contains the expected path
    framework.assert_output_contains(["default/services"])


if __name__ == "__main__":
    run_test(test_pwd_after_cd, "after-cd", "pwd", expected_items=["/default/services"])
