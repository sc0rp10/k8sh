#!/usr/bin/env python3
"""
Test for the ls command to verify it doesn't show error messages when restoring the original path
"""


def test_ls_no_error_on_path_restore(framework):
    """Test that the ls command doesn't show error messages when restoring the original path"""
    # Navigate to a path and then use ls with a path argument
    framework.run_test_commands([
        "cd default/deployments",
        "ls example-deployment",
        "pwd"  # Add pwd to verify we're still in the correct directory
    ])

    # Verify that no error messages are shown
    framework.assert_output_not_contains(["Error executing command: Invalid segment"])

    # Verify that we're still in the correct directory after the ls command
    framework.assert_output_contains(["default/deployments"])
