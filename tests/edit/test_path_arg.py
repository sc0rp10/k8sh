#!/usr/bin/env python3
"""
Test for the edit command with path arguments
"""


def test_edit_absolute_path(framework):
    """Test edit command with an absolute path"""
    # Run the edit command with an absolute path
    framework.run_test_commands([
        "edit /kube-system/services/kube-dns"
    ])

    # Assert that the correct message was printed
    framework.assert_output_contains([
        "Would run: EDITOR=mock-editor kubectl edit services kube-dns -n kube-system"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error: Failed to edit resource",
        "Error: kubectl command not found"
    ])


def test_edit_relative_path(framework):
    """Test edit command with a relative path"""
    # Run the edit command with a relative path
    framework.run_test_commands([
        "cd /default/services",
        "edit kubernetes"
    ])

    # Assert that the correct message was printed
    framework.assert_output_contains([
        "Would run: EDITOR=mock-editor kubectl edit services kubernetes -n default"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error: Failed to edit resource",
        "Error: kubectl command not found"
    ])
