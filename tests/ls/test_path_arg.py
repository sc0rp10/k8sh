#!/usr/bin/env python3
"""
Test for the ls command with a path argument
"""
from tests.common.test_framework import K8shTestFramework, run_test


def test_ls_path_arg(framework: K8shTestFramework) -> None:
    """Test the ls command with a path argument"""
    framework.run_test_commands(["ls default/services"])

    # Check if the output contains the path
    framework.assert_output_contains(["default/services"])


if __name__ == "__main__":
    run_test(test_ls_path_arg, "path-arg", "ls", expected_items=["default/services"])
