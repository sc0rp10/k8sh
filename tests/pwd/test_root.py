#!/usr/bin/env python3
"""
Test for the pwd command at root level
"""
from tests.common.test_framework import K8shTestFramework, run_test


def test_pwd_root(framework: K8shTestFramework) -> None:
    """Test the pwd command at root level"""
    framework.run_test_commands(["pwd"])

    # Check if the output contains the root path
    framework.assert_output_contains(["$ pwd", ""])


if __name__ == "__main__":
    run_test(test_pwd_root, "root", "pwd", expected_items=["$ pwd", "/"])
