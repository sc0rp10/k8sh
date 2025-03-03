#!/usr/bin/env python3
"""
Test the --no-color flag
"""
import os
import subprocess


def test_no_color_flag():
    """Test that the --no-color flag disables colors"""
    # Run with colors (default)
    env = os.environ.copy()
    env["K8SH_MOCK"] = "1"
    process_with_color = subprocess.Popen(
        ["python3", "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        universal_newlines=True,
    )
    process_with_color.stdin.write("help\nexit\n")
    process_with_color.stdin.flush()
    output_with_color, _ = process_with_color.communicate(timeout=2)

    # Run with --no-color flag
    process_no_color = subprocess.Popen(
        ["python3", "main.py", "--no-color"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        universal_newlines=True,
    )
    process_no_color.stdin.write("help\nexit\n")
    process_no_color.stdin.flush()
    output_no_color, _ = process_no_color.communicate(timeout=2)

    # Check that the colored output contains ANSI escape sequences
    assert "\033[" in output_with_color, "Colored output should contain ANSI escape sequences"

    # Check that the non-colored output does not contain ANSI escape sequences
    assert "\033[" not in output_no_color, "Non-colored output should not contain ANSI escape sequences"
