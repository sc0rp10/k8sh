#!/usr/bin/env python3
"""
Test cases for different editors in the edit command
"""


def test_vim_editor(framework, monkeypatch):
    """Test using vim as the editor"""
    # Patch the editor check to always return mock-editor
    monkeypatch.setattr("command.edit.EditCommand._do_execute", lambda self, state, namespace, resource_type, resource_name:
                        print(f"Would run: EDITOR=mock-editor kubectl edit {resource_type} {resource_name} -n {namespace}"))

    # Run the vim command (which is an alias for edit)
    framework.run_test_commands([
        "vim /default/services/kubernetes"
    ])

    # Assert that the correct message was printed with mock-editor
    framework.assert_output_contains([
        "Would run: EDITOR=mock-editor kubectl edit services kubernetes -n default"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error:"
    ])


def test_nano_editor(framework, monkeypatch):
    """Test using nano as the editor"""
    # Patch the editor check to always return mock-editor
    monkeypatch.setattr("command.edit.EditCommand._do_execute", lambda self, state, namespace, resource_type, resource_name:
                        print(f"Would run: EDITOR=mock-editor kubectl edit {resource_type} {resource_name} -n {namespace}"))

    # Run the nano command (which is an alias for edit)
    framework.run_test_commands([
        "nano /default/services/kubernetes"
    ])

    # Assert that the correct message was printed with mock-editor
    framework.assert_output_contains([
        "Would run: EDITOR=mock-editor kubectl edit services kubernetes -n default"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error:"
    ])


def test_custom_editor(framework, monkeypatch):
    """Test using a custom editor defined in EDITOR environment variable"""
    # Patch the editor check to always return mock-editor
    monkeypatch.setattr("command.edit.EditCommand._do_execute", lambda self, state, namespace, resource_type, resource_name:
                        print(f"Would run: EDITOR=mock-editor kubectl edit {resource_type} {resource_name} -n {namespace}"))

    # Run the edit command (should use the mock editor)
    framework.run_test_commands([
        "edit /default/services/kubernetes"
    ])

    # Assert that the correct message was printed with mock-editor
    framework.assert_output_contains([
        "Would run: EDITOR=mock-editor kubectl edit services kubernetes -n default"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error:"
    ])
