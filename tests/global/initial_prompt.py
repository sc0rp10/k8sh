#!/usr/bin/env python3
"""
Test for the initial prompt of K8sh
"""

import pytest
from tests.common.test_framework import K8shTestFramework, run_test


@pytest.fixture
def framework():
    """Create and return a test framework instance"""
    return K8shTestFramework()


def test_initial_prompt(framework):
    """Test the initial prompt of K8sh"""
    # Start the shell
    framework.start_shell()

    # No commands needed, just check the prompt
    framework.run_test_commands([])

    # Check if the output contains the expected prompt
    framework.assert_output_contains(["Using mock Kubernetes client", "$"])


if __name__ == "__main__":
    run_test(
        test_initial_prompt,
        "initial-prompt",
        "global",
        expected_items=["Using mock Kubernetes client", "$"]
    )
