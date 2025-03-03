#!/usr/bin/env python3
"""
Test for the initial prompt of K8sh
"""

from tests.common.test_framework import K8shTestFramework, run_test


def test_initial_prompt(framework: K8shTestFramework) -> None:
    """Test the initial prompt of K8sh"""
    framework.run_test_commands([])  # No commands needed, just check the prompt

    # Check if the output contains the expected prompt
    framework.assert_output_contains(["Using mock Kubernetes client", "$"])


if __name__ == "__main__":
    run_test(
        test_initial_prompt,
        "initial-prompt",
        "global",
        expected_items=["Using mock Kubernetes client", "$"]
    )
