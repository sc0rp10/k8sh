#!/usr/bin/env python3
"""
Test for the cd command with a path argument
"""
from tests.common.test_framework import K8shTestFramework, run_test


def test_cd_path_arg(framework: K8shTestFramework) -> None:
    """Test the cd command with a path argument"""
    framework.run_test_commands(["cd default/services", "pwd"])

    # Check if the output contains the expected path
    framework.assert_output_contains(["default/services"])


if __name__ == "__main__":
    run_test(test_cd_path_arg, "path-arg", "cd", expected_items=["/default/services"])
