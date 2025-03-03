#!/usr/bin/env python3
"""
Test cases for different editors in the edit command
"""
import os

from tests.conftest import K8shTestFramework


def test_vim_editor(framework: K8shTestFramework) -> None:
    """Test using vim as the editor"""
    # Run the vim command (which is an alias for edit)
    framework.run_test_commands([
        "vim /default/services/kubernetes"
    ])

    # Assert that the correct message was printed with vim as the editor
    framework.assert_output_contains([
        "Would run: EDITOR=vim kubectl edit services kubernetes -n default"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error:"
    ])


def test_nano_editor(framework: K8shTestFramework) -> None:
    """Test using nano as the editor"""
    # Run the nano command (which is an alias for edit)
    framework.run_test_commands([
        "nano /default/services/kubernetes"
    ])

    # Assert that the correct message was printed with nano as the editor
    framework.assert_output_contains([
        "Would run: EDITOR=nano kubectl edit services kubernetes -n default"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error:"
    ])


def test_custom_editor(framework: K8shTestFramework) -> None:
    """Test using a custom editor defined in EDITOR environment variable"""
    # Set a custom editor in the environment
    old_env = os.environ.copy()
    try:
        os.environ["EDITOR"] = "code"

        # Create a new framework with the updated environment
        custom_framework = K8shTestFramework()

        # Run the edit command (should use the EDITOR env var)
        custom_framework.run_test_commands([
            "edit /default/services/kubernetes"
        ])

        # Assert that the correct message was printed with the custom editor
        custom_framework.assert_output_contains([
            "Would run: EDITOR=code kubectl edit services kubernetes -n default"
        ])

        # Assert that no error message was printed
        custom_framework.assert_output_not_contains([
            "Error:"
        ])
    finally:
        # Restore the original environment
        os.environ.clear()
        os.environ.update(old_env)
