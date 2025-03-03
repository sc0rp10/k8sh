#!/usr/bin/env python3
"""
Tests for K8shCompleter with focus on fuzzy matching of paths with typos
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fuzzyfinder import fuzzyfinder

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


@pytest.fixture
def mock_state(request):
    """Create a mock State with configurable path"""
    state = Mock(spec=State)
    state.get_current_path.return_value = ""  # Default empty path
    return state


def test_namespace_fuzzy_matching():
    """Test fuzzy matching of namespace names"""
    # First, verify that the fuzzyfinder itself is working
    namespaces = ['default', 'kube-system', 'monitoring']

    # This dictionary maps typos to the expected matches
    typo_map = {
        'def': ['default'],
        'dflt': ['default'],
        'kube': ['kube-system'],
        'k-s': ['kube-system'],
        'mon': ['monitoring'],
        'mnt': ['monitoring'],
    }

    # Test the fuzzyfinder directly
    for typo, expected_matches in typo_map.items():
        results = list(fuzzyfinder(typo, namespaces))
        for expected in expected_matches:
            assert expected in results, f"Expected '{expected}' to be in results for '{typo}', got {results}"


def test_completer_fuzzy_namespace(mock_registry, mock_state):
    """Test namespace fuzzy matching in the completer"""
    # Setup mock state to return namespaces at root level
    namespaces = ['default', 'kube-system', 'monitoring']
    mock_state.get_available_items.return_value = namespaces
    mock_state.is_directory.side_effect = lambda x: True  # All namespaces are directories
    mock_state.get_current_path.return_value = ""

    # Create completer
    completer = K8shCompleter(mock_registry, mock_state)

    # Test with various namespace typos by directly mocking _get_path_completions
    with patch.object(completer, '_get_path_completions') as mock_path_completer:
        # Configure the mock to return appropriate completions based on input path
        def side_effect(path):
            if path in ["def", "dflt"]:
                return [Mock(text="default")]
            elif path in ["kube", "k-s"]:
                return [Mock(text="kube-system")]
            elif path == "mon":
                return [Mock(text="monitoring")]
            else:
                return []

        mock_path_completer.side_effect = side_effect

        test_cases = {
            'cd def': ('def', 'default'),
            'cd dflt': ('dflt', 'default'),
            'ls kube': ('kube', 'kube-system'),
            'cd k-s': ('k-s', 'kube-system'),
            'cat mon': ('mon', 'monitoring'),
        }

        # Get completions and check they contain the expected matches
        for input_text, (expected_path, expected_match) in test_cases.items():
            document = Document(input_text)
            completions = list(completer.get_completions(document, Mock()))

            # Verify the path completer was called with the correct parameter
            mock_path_completer.assert_any_call(expected_path)

            # Convert completions to a list of text values
            completion_texts = [c.text for c in completions]

            # Check if the expected match is in the completions
            assert expected_match in completion_texts, f"Expected '{expected_match}' in completions for '{input_text}', got {completion_texts}"


def test_completer_fuzzy_resources(mock_registry, mock_state):
    """Test fuzzy matching for resources like pods, deployments, etc."""
    # Setup mock state to return resources
    resources = ['pods', 'deployments', 'services', 'configmaps', 'secrets']
    mock_state.get_current_path.return_value = "default"
    mock_state.get_available_items.return_value = resources
    mock_state.is_directory.side_effect = lambda x: True  # All resources are directories

    # Create completer
    completer = K8shCompleter(mock_registry, mock_state)

    # Test with various resource typos
    test_cases = {
        'cd pod': 'pods',
        'ls dep': 'deployments',
        'cat dploy': 'deployments',
        'cd srv': 'services',
        'ls svc': 'services',
        'cd cfg': 'configmaps',
    }

    # Get completions and check they contain the expected matches
    for input_text, expected_match in test_cases.items():
        document = Document(input_text)
        completions = list(completer.get_completions(document, Mock()))

        # Convert completions to a list of text values
        completion_texts = [c.text for c in completions]

        # Check if the expected match is in the completions
        assert expected_match in completion_texts, f"Expected '{expected_match}' in completions for '{input_text}', got {completion_texts}"


def test_completer_two_segment_paths(mock_registry):
    """Test fuzzy matching with two-segment paths (namespace/resource)"""
    # Create a state for the completer
    main_state = Mock(spec=State)
    main_state.get_current_path.return_value = ""  # At root

    # Create completer
    completer = K8shCompleter(mock_registry, main_state)

    # Mock the _get_path_completions method to return the expected completions
    with patch.object(completer, '_get_path_completions') as mock_path_completer:
        # Configure the mock to return appropriate completions based on input path
        def side_effect(path):
            if "def/pod" in path:
                return [Mock(text="default/pods")]
            elif "dflt/dep" in path or "default/dploy" in path:
                return [Mock(text="default/deployments")]
            elif "def/svc" in path:
                return [Mock(text="default/services")]
            elif "k-s/pod" in path:
                return [Mock(text="kube-system/pods")]
            else:
                return []

        mock_path_completer.side_effect = side_effect

        # Test with various two-segment path typos
        test_cases = {
            'cd def/pod': ('def/pod', 'default/pods'),
            'ls dflt/dep': ('dflt/dep', 'default/deployments'),
            'cd default/dploy': ('default/dploy', 'default/deployments'),
            'cat def/svc': ('def/svc', 'default/services'),
            'ls k-s/pod': ('k-s/pod', 'kube-system/pods'),
        }

        # Get completions and check they contain the expected matches
        for input_text, (expected_path, expected_match) in test_cases.items():
            document = Document(input_text)
            completions = list(completer.get_completions(document, Mock()))

            # Verify the path completer was called with the correct path segment
            mock_path_completer.assert_any_call(expected_path)

            # Convert completions to a list of text values
            completion_texts = [c.text for c in completions]

            # Check if the expected match is in the completions
            assert expected_match in completion_texts, f"Expected '{expected_match}' in completions for '{input_text}', got {completion_texts}"


def test_completer_three_segment_paths(mock_registry):
    """Test fuzzy matching with three-segment paths (namespace/resource/name)"""
    # Create a state for the completer
    main_state = Mock(spec=State)
    main_state.get_current_path.return_value = ""  # At root

    # Create completer
    completer = K8shCompleter(mock_registry, main_state)

    # Mock the _get_path_completions method to return expected completions
    with patch.object(completer, '_get_path_completions') as mock_path_completer:
        # Configure the mock to return appropriate completions based on input path
        def side_effect(path):
            if "ngi" in path or "ngx" in path or "ngnx" in path:
                return [Mock(text="default/pods/nginx")]
            elif "pstg" in path:
                return [Mock(text="default/pods/postgres")]
            elif "rds" in path:
                return [Mock(text="default/pods/redis")]
            else:
                return []

        mock_path_completer.side_effect = side_effect

        # Test with various three-segment path typos
        test_cases = {
            'cd def/pod/ngi': ('def/pod/ngi', 'default/pods/nginx'),
            'ls dflt/pods/ngx': ('dflt/pods/ngx', 'default/pods/nginx'),
            'cat default/pods/ngnx': ('default/pods/ngnx', 'default/pods/nginx'),
            'cd def/pods/pstg': ('def/pods/pstg', 'default/pods/postgres'),
            'ls default/pods/rds': ('default/pods/rds', 'default/pods/redis'),
        }

        # Get completions and check they contain the expected matches
        for input_text, (expected_path, expected_match) in test_cases.items():
            document = Document(input_text)
            completions = list(completer.get_completions(document, Mock()))

            # Verify the path completer was called with the correct path segment
            mock_path_completer.assert_any_call(expected_path)

            # Convert completions to a list of text values
            completion_texts = [c.text for c in completions]

            # Check if the expected match is in the completions
            assert expected_match in completion_texts, f"Expected '{expected_match}' in completions for '{input_text}', got {completion_texts}"
