#!/usr/bin/env python3
"""
Test for the cat command on a namespace resource
"""
import os
import sys


def test_cat_namespace(framework):
    """Test the cat command on a namespace resource"""
    # Cat the default namespace from the root
    framework.run_test_commands([
        "cat /default"
    ])

    # Print the output for debugging if DEBUG=1 is set
    if os.environ.get("DEBUG") == "1" and framework.output:
        print("DEBUG OUTPUT:", file=sys.stderr)
        print(framework.output, file=sys.stderr)

    # Check if the output contains expected YAML elements
    framework.assert_output_contains([
        "apiVersion",
        "kind",
        "Namespace",
        "metadata",
        "name",
        "default"
    ])
