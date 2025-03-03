#!/usr/bin/env python3
"""
Test for the cat command error cases
"""
import os
import sys


def test_cat_error(framework):
    """Test the cat command error cases"""
    # Try to cat a non-existent resource
    framework.run_test_commands([
        "cat /nonexistent"
    ])

    # Print the output for debugging if DEBUG=1 is set
    if os.environ.get("DEBUG") == "1" and framework.output:
        print("DEBUG OUTPUT:", file=sys.stderr)
        print(framework.output, file=sys.stderr)

    # Check if the output contains the error message
    framework.assert_output_contains([
        "Error: Could not get YAML definition for namespace/nonexistent"
    ])


def test_cat_no_args(framework):
    """Test the cat command with no arguments"""
    # Try to cat without arguments
    framework.run_test_commands([
        "cat"
    ])

    # Check if the output contains the error message
    framework.assert_output_contains([
        "Error: No filename provided"
    ])
