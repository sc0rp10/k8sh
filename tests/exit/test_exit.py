#!/usr/bin/env python3
"""
Test for the exit command
"""
from tests.common.test_framework import K8shTestFramework, run_test


def test_exit(framework: K8shTestFramework) -> None:
    """Test the exit command"""
    framework.run_test_commands([])  # No commands needed, exit is automatic

    # Check if the output contains the exit message
    framework.assert_output_contains(["Exiting shell"])


if __name__ == "__main__":
    run_test(test_exit, "exit", "exit", expected_items=["Exiting shell"])
