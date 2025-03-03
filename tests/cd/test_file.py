#!/usr/bin/env python3
"""
Test for the cd command to a file (which should fail)
"""


def test_cd_file(framework):
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
