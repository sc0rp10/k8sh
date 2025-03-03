#!/usr/bin/env python3
"""
Test for the edit command on a namespace resource
"""


def test_edit_namespace(framework):
    """Test edit command on a namespace resource"""
    # Run the edit command
    framework.run_test_commands([
        "cd /",
        "edit default"
    ])

    # Assert that the correct message was printed
    framework.assert_output_contains([
        "Would run: EDITOR=vim kubectl edit namespace default -n"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error:"
    ])
