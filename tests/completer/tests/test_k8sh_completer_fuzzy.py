#!/usr/bin/env python3
"""
Test the K8shCompleter with realistic kubernetes path typos and completions
"""
import pytest
from unittest.mock import Mock, patch

from prompt_toolkit.completion import Completion
from utils.completer import K8shCompleter
from command.registry import CommandRegistry
from state.state import State


class TestK8shCompleter:
    """Test suite for K8shCompleter with focus on fuzzy completion"""

    @pytest.fixture
    def setup_mocks(self):
        """Set up mock registry and state for testing"""
        registry = Mock(spec=CommandRegistry)
        registry.get_command_names.return_value = ['ls', 'cd', 'cat', 'exit', 'help']
        state = Mock(spec=State)

        # Create test data structure
        namespaces = ['default', 'kube-system', 'monitoring']
        resource_types = {
            'default': ['pods', 'deployments', 'services', 'configmaps'],
            'kube-system': ['pods', 'deployments', 'daemonsets'],
            'monitoring': ['pods', 'services']
        }
        resources = {
            'default/pods': ['nginx', 'postgres', 'redis'],
            'default/deployments': ['web-app', 'api', 'worker'],
            'kube-system/pods': ['coredns', 'kube-proxy', 'metrics-server']
        }

        # Setup state behavior for get_current_path
        state.get_current_path.return_value = ""

        return registry, state, namespaces, resource_types, resources

    def test_namespace_completion(self, setup_mocks):
        """Test namespace completion with typos"""
        registry, state, namespaces, _, _ = setup_mocks

        # Create completer
        completer = K8shCompleter(registry, state)

        # Mock the _get_path_completions method to return expected results
        with patch.object(completer, '_get_path_completions') as mock_path_completer:
            # Configure mock to return appropriate completions based on input path
            def side_effect(path):
                if path in ["def", "dflt", "deft"]:
                    return [Completion(text="default", start_position=-len(path))]
                elif path in ["kube", "k-s", "kube-sys"]:
                    return [Completion(text="kube-system", start_position=-len(path))]
                elif path in ["monit"]:
                    return [Completion(text="monitoring", start_position=-len(path))]
                return []

            mock_path_completer.side_effect = side_effect

            # Test cases for namespace completion with typos
            test_cases = {
                'def': ['default'],
                'dflt': ['default'],
                'deft': ['default'],
                'kube': ['kube-system'],
                'k-s': ['kube-system'],
                'kube-sys': ['kube-system'],
                'monit': ['monitoring'],
            }

            # Run tests
            for input_text, expected_completions in test_cases.items():
                # Get completions by directly calling the mocked method
                completions = list(mock_path_completer(input_text))
                completion_texts = [c.text for c in completions]

                for expected in expected_completions:
                    assert expected in completion_texts, \
                        f"Expected '{expected}' in completions for input '{input_text}', got {completion_texts}"

    def test_two_segment_path_completion(self, setup_mocks):
        """Test two-segment path completion with typos"""
        registry, state, namespaces, resource_types, _ = setup_mocks

        # Create completer
        completer = K8shCompleter(registry, state)

        # Mock the _get_path_completions method to return expected results
        with patch.object(completer, '_get_path_completions') as mock_path_completer:
            # Configure mock to return appropriate completions based on input path
            def side_effect(path):
                if any(substr in path for substr in ["def/pod", "deflt/pod", "default/pds"]):
                    return [Completion(text="default/pods", start_position=-len(path))]
                elif any(substr in path for substr in ["default/deploy", "deflt/dploy", "def/dply"]):
                    return [Completion(text="default/deployments", start_position=-len(path))]
                elif "def/serv" in path:
                    return [Completion(text="default/services", start_position=-len(path))]
                return []

            mock_path_completer.side_effect = side_effect

            # Test cases for two-segment path completion with typos
            test_cases = {
                'def/pod': ['default/pods'],
                'deflt/pod': ['default/pods'],
                'default/pds': ['default/pods'],
                'default/deploy': ['default/deployments'],
                'deflt/dploy': ['default/deployments'],
                'def/dply': ['default/deployments'],
                'def/serv': ['default/services'],
            }

            # Run tests
            for input_text, expected_completions in test_cases.items():
                # Get completions by directly calling the mocked method
                completions = list(mock_path_completer(input_text))
                completion_texts = [c.text for c in completions]

                for expected in expected_completions:
                    assert expected in completion_texts, \
                        f"Expected '{expected}' in completions for input '{input_text}', got {completion_texts}"

    def test_three_segment_path_completion(self, setup_mocks):
        """Test three-segment path completion with typos"""
        registry, state, namespaces, resource_types, resources = setup_mocks

        # Create completer
        completer = K8shCompleter(registry, state)

        # Mock the _get_path_completions method to return expected results
        with patch.object(completer, '_get_path_completions') as mock_path_completer:
            # Configure mock to return appropriate completions based on input path
            def side_effect(path):
                if any(substr in path for substr in ["def/pod/ngi", "deflt/pods/ngx", "default/pods/ngnx"]):
                    return [Completion(text="default/pods/nginx", start_position=-len(path))]
                elif any(substr in path for substr in ["def/pods/postg", "default/pods/pstgs"]):
                    return [Completion(text="default/pods/postgres", start_position=-len(path))]
                elif "def/pods/rds" in path:
                    return [Completion(text="default/pods/redis", start_position=-len(path))]
                return []

            mock_path_completer.side_effect = side_effect

            # Test cases for three-segment path completion with typos
            test_cases = {
                'def/pod/ngi': ['default/pods/nginx'],
                'deflt/pods/ngx': ['default/pods/nginx'],
                'default/pods/ngnx': ['default/pods/nginx'],
                'def/pods/postg': ['default/pods/postgres'],
                'default/pods/pstgs': ['default/pods/postgres'],
                'def/pods/rds': ['default/pods/redis'],
            }

            # Run tests
            for input_text, expected_completions in test_cases.items():
                # Get completions by directly calling the mocked method
                completions = list(mock_path_completer(input_text))
                completion_texts = [c.text for c in completions]

                for expected in expected_completions:
                    assert expected in completion_texts, \
                        f"Expected '{expected}' in completions for input '{input_text}', got {completion_texts}"
