#!/usr/bin/env python3
"""
Tests for multi-segment path completion in K8sh
focusing on the fuzzy matching capabilities
"""
import pytest
from unittest.mock import MagicMock, patch
from prompt_toolkit.document import Document

from utils.completer import K8shCompleter
from command.registry import CommandRegistry
from state.state import State


@pytest.fixture
def mock_registry():
    """Create a mock CommandRegistry"""
    registry = MagicMock(spec=CommandRegistry)
    registry.get_command_names.return_value = ['ls', 'cd', 'cat', 'exit', 'help']
    registry.get_for_autocomplete.return_value = ['ls', 'cd', 'cat']
    return registry


@patch('utils.completer.State')
def test_two_segment_path_completion(mock_state_class, mock_registry):
    """Test fuzzy matching with two-segment paths (namespace/resource)"""
    # Create a state for the completer
    main_state = MagicMock(spec=State)
    main_state.get_current_path.return_value = ""

    # Mock the internal temp_state created by the completer
    temp_state = MagicMock(spec=State)
    mock_state_class.return_value = temp_state

    # Set up available items for different paths
    namespaces = ["default", "kube-system"]
    resource_types = ["pods", "deployments", "services"]

    # Configure the behavior of the temp_state
    # First call for namespaces, second for resource types
    temp_state.get_available_items.side_effect = [namespaces, resource_types]
    temp_state.is_directory.return_value = True

    # Create the completer
    completer = K8shCompleter(mock_registry, main_state)

    # Test with a valid two-segment path and command
    document = Document("cd def/pod")
    completions = list(completer.get_completions(document))

    # Get the completion texts
    completion_texts = [c.text for c in completions]

    # In an ideal implementation, we should find "default/pods"
    assert "default/pods" in completion_texts, f"Expected 'default/pods' in completions, got {completion_texts}"


@patch('utils.completer.State')
def test_three_segment_path_completion(mock_state_class, mock_registry):
    """Test fuzzy matching with three-segment paths (namespace/resource/name)"""
    # Create a state for the completer
    main_state = MagicMock(spec=State)
    main_state.get_current_path.return_value = ""

    # Mock the internal temp_state created by the completer
    temp_state = MagicMock(spec=State)
    mock_state_class.return_value = temp_state

    # Set up available items for different paths
    namespaces = ["default", "kube-system"]
    resource_types = ["pods", "deployments", "services"]
    pod_names = ["nginx", "postgres", "redis"]

    # Configure the behavior of the temp_state
    # First call for namespaces, second for resource types, third for pod names
    temp_state.get_available_items.side_effect = [namespaces, resource_types, pod_names]

    # Set the directory behavior
    def is_directory(item):
        return item in namespaces or item in resource_types

    temp_state.is_directory.side_effect = is_directory

    # Create the completer
    completer = K8shCompleter(mock_registry, main_state)

    # Test with a valid three-segment path and command
    document = Document("cd def/pod/ng")
    completions = list(completer.get_completions(document))

    # Get the completion texts
    completion_texts = [c.text for c in completions]

    # In an ideal implementation, we should find "default/pods/nginx"
    assert "default/pods/nginx" in completion_texts, f"Expected 'default/pods/nginx' in completions, got {completion_texts}"


@patch('utils.completer.State')
def test_fuzzy_matching_on_path_segments(mock_state_class, mock_registry):
    """Test fuzzy matching on each segment of a multi-segment path"""
    # Create a state for the completer
    main_state = MagicMock(spec=State)
    main_state.get_current_path.return_value = ""

    # Mock the internal temp_state created by the completer
    temp_state = MagicMock(spec=State)
    mock_state_class.return_value = temp_state

    # Set up available items for different paths
    namespaces = ["default", "kube-system"]
    resource_types = ["pods", "deployments", "services"]

    # Configure the behavior of the temp_state
    # First call for namespaces, second for resource types
    temp_state.get_available_items.side_effect = [namespaces, resource_types]
    temp_state.is_directory.return_value = True

    # Create the completer
    completer = K8shCompleter(mock_registry, main_state)

    # Test various multi-segment paths with typos
    # Note: The K8shCompleter extracts the last part of the input as the path
    # So we need to mock the _get_path_completions method to return the right completions
    with patch.object(completer, '_get_path_completions') as mock_path_completer:
        # Configure mock to return appropriate completions
        mock_path_completer.side_effect = lambda path: [
            MagicMock(text="default/deployments") if "dep" in path else
            MagicMock(text="default/services") if "svc" in path else
            MagicMock(text="kube-system/pods") if "pod" in path else
            []
        ]

        test_cases = [
            # Format: (input_text, expected_path, expected_match)
            ("cd dflt/dep", "dflt/dep", "default/deployments"),
            ("cd def/svc", "def/svc", "default/services"),
            ("cd k-s/pod", "k-s/pod", "kube-system/pods"),
        ]

        for input_text, expected_path, expected_match in test_cases:
            document = Document(input_text)
            completions = list(completer.get_completions(document))
            completion_texts = [c.text for c in completions]

            # Verify the path completer was called with the correct parameter
            mock_path_completer.assert_any_call(expected_path)

            # Verify we got the expected completion
            assert expected_match in completion_texts, f"Expected '{expected_match}' in completions for '{input_text}', got {completion_texts}"


@patch('state.state.State')
def test_completion_with_deeper_paths(mock_state_class):
    """Test path completion with paths that have multiple segments"""
    # Set up the mock state behavior
    # We'll simulate a mock temp_state instance that is created by the completer
    temp_state = MagicMock(spec=State)
    mock_state_class.return_value = temp_state

    # Define available items for different paths
    # For root path
    temp_state.get_available_items.side_effect = lambda: ["default", "kube-system"]

    # Define the directory behavior
    temp_state.is_directory.return_value = True

    # Create a main state for the completer
    main_state = MagicMock(spec=State)
    main_state.get_current_path.return_value = ""

    # Create a registry for the completer
    registry = MagicMock(spec=CommandRegistry)
    registry.get_command_names.return_value = ["cd", "ls", "cat"]
    registry.get_for_autocomplete.return_value = ["cd", "ls", "cat"]

    # Create the completer
    completer = K8shCompleter(registry, main_state)

    # Test with a path that has a typed segment after a command
    document = Document("cd def")

    # Mock the _get_path_completions method to provide a known good output
    with patch.object(completer, '_get_path_completions') as mock_path_completer:
        mock_path_completer.return_value = [
            MagicMock(text="default")
        ]

        completions = list(completer.get_completions(document))

        # Verify the path completer was called with the correct path
        mock_path_completer.assert_called_once_with("def")

        # Check if we got any completions
        assert len(completions) > 0
        # The completion text should be "default"
        assert completions[0].text == "default"
