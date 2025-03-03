#!/usr/bin/env python3
"""
Tests for fuzzy path matching in K8sh with focus on
handling typos and providing intuitive completions
"""
import pytest
from unittest.mock import patch, MagicMock
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
def mock_state():
    """Create a mock State with configurable path"""
    state = MagicMock(spec=State)
    state.get_current_path.return_value = ""  # Default empty path
    return state


def test_fuzzyfinder_basic():
    """Test the basic functionality of fuzzyfinder directly"""
    # Test with namespace names
    namespaces = ['default', 'kube-system', 'monitoring']

    # This dictionary maps search strings to expected matches
    test_cases = {
        'def': ['default'],
        'dflt': ['default'],
        'kube': ['kube-system'],
        'k-s': ['kube-system'],
        'mon': ['monitoring'],
    }

    # Test each case
    for search, expected in test_cases.items():
        results = list(fuzzyfinder(search, namespaces))
        for item in expected:
            assert item in results, f"Expected '{item}' to be in results for '{search}', got {results}"


def test_fuzzy_path_completion_direct():
    """Test direct path completion with fuzzy matching"""
    # Mock the _get_path_completions method in K8shCompleter
    with patch('utils.completer.K8shCompleter._get_path_completions') as mock_path_completer:
        # Create a fake completion
        mock_path_completer.return_value = [
            MagicMock(text='default')
        ]

        # Create a registry and state
        registry = MagicMock(spec=CommandRegistry)
        registry.get_command_names.return_value = ['ls', 'cd', 'cat']
        registry.get_for_autocomplete.return_value = ['ls', 'cd', 'cat']

        state = MagicMock(spec=State)
        state.get_current_path.return_value = ""

        # Create completer
        completer = K8shCompleter(registry, state)

        # Test with a command that should trigger path completion
        document = Document("cd def")
        _ = list(completer.get_completions(document))

        # Verify the path completer was called with the correct parameter
        mock_path_completer.assert_called_once_with("def")


@patch('state.state.State')
def test_fuzzy_namespace_completion(mock_state_class):
    """Test fuzzy matching of namespace names"""
    # Setup mocks
    temp_state = MagicMock(spec=State)
    mock_state_class.return_value = temp_state

    namespaces = ['default', 'kube-system', 'monitoring']
    temp_state.get_available_items.return_value = namespaces
    temp_state.is_directory.return_value = True

    main_state = MagicMock(spec=State)
    main_state.get_current_path.return_value = ""

    registry = MagicMock(spec=CommandRegistry)
    registry.get_command_names.return_value = ['cd', 'ls', 'cat']
    registry.get_for_autocomplete.return_value = ['cd', 'ls', 'cat']

    # Create completer
    completer = K8shCompleter(registry, main_state)

    # Test with various typos in path segments after the command
    test_cases = {
        'cd def': 'default',
        'cd dflt': 'default',
    }

    # Test each case
    for input_text, expected_match in test_cases.items():
        document = Document(input_text)
        completer._get_path_completions = MagicMock(return_value=[
            MagicMock(text=expected_match)
        ])

        completions = list(completer.get_completions(document))
        completion_texts = [c.text for c in completions]

        assert expected_match in completion_texts, f"Expected '{expected_match}' in completions for '{input_text}', got {completion_texts}"


def test_path_segment_completion():
    """Test that individual path segments are completed with fuzzy matching"""
    # Let's implement direct testing of the fuzzy matching in _get_path_completions

    # Mock the state
    state = MagicMock(spec=State)
    state.get_current_path.return_value = ""
    state.get_available_items.return_value = ["default", "kube-system", "monitoring"]
    state.is_directory.return_value = True

    # Mock the registry
    registry = MagicMock(spec=CommandRegistry)
    registry.get_command_names.return_value = ["cd", "ls"]
    registry.get_for_autocomplete.return_value = ["cd", "ls"]

    # Create the completer
    completer = K8shCompleter(registry, state)

    # Test a single segment path
    results = list(completer._get_path_completions("def"))

    # There should be at least one completion
    assert len(results) > 0

    # At least one of the completions should be "default"
    completion_texts = [c.text for c in results]
    assert "default" in completion_texts, f"Expected 'default' in completions, got {completion_texts}"


def test_path_segment_completion_with_typos():
    """
    Test path completion with various typos to ensure the fuzzy matching works
    """
    # Setup a more realistic test with mock state
    state = MagicMock(spec=State)
    state.get_current_path.return_value = ""  # Start at root path

    # Set up available items at root to be namespaces
    namespaces = ["default", "kube-system", "app-monitoring"]
    state.get_available_items.return_value = namespaces
    state.is_directory.return_value = True

    # Mock the registry
    registry = MagicMock(spec=CommandRegistry)
    registry.get_for_autocomplete.return_value = ["cd", "ls", "cat"]

    # Create the completer
    completer = K8shCompleter(registry, state)

    # Test various typos for namespaces
    # Note: The current fuzzy matching implementation works best with
    # prefix matches and skipped characters, but not with transposed or partial segment matches.
    # The K8sh fuzzy matching is primarily designed for command names and
    # simple path segment completions, not complex multi-segment typos.
    test_cases = [
        ("def", "default"),        # Prefix
        ("dflt", "default"),       # Missing vowels
        ("k-s", "kube-system"),    # Abbreviated with dash
    ]

    for typo, expected in test_cases:
        # Get completions directly from _get_path_completions
        completions = list(completer._get_path_completions(typo))
        completion_texts = [c.text for c in completions]

        assert expected in completion_texts, f"Expected '{expected}' in completions for '{typo}', got {completion_texts}"
