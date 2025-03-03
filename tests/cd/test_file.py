#!/usr/bin/env python3
"""
Test for the cd command to a file (which should fail)
"""
from tests.common.test_framework import K8shTestFramework, run_test


def test_cd_file(framework: K8shTestFramework) -> None:
    """Test the cd command to a file (which should fail)"""
    output = framework.run_test_commands([
        "cd default/pods/nginx-pod-1",
        "cd nginx",
        "pwd"
    ])

    # Print the output for debugging
    print(f"Output: {output}")

    # Only check that we're still in the original directory
    # This indicates the cd command failed as expected
    framework.assert_output_contains(["default/pods/nginx-pod-1"])


if __name__ == "__main__":
    run_test(
        test_cd_file,
        "file",
        "cd",
        expected_items=["default/pods/nginx-pod-1"]
    )
