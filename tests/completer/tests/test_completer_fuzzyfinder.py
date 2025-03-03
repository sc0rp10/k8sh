#!/usr/bin/env python3
"""
Simple tests for the fuzzyfinder functionality used in K8sh's autocompletion
"""
from fuzzyfinder import fuzzyfinder


def test_basic_fuzzy_matching():
    """Test basic fuzzy matching with simple cases"""
    test_cases = {
        'def': ['default'],
        'dflt': ['default'],
        'kube': ['kube-system'],
        'kbs': ['kube-system'],
        'mon': ['monitoring'],
        'mnt': ['monitoring'],
        'dft': ['default'],  # More challenging abbreviation
        'k-s': ['kube-system'],  # With hyphen
        'k-system': ['kube-system'],  # Partial match with hyphen
        'm': ['monitoring'],  # Single letter
    }

    collection = ['default', 'kube-system', 'monitoring']

    for input_text, expected_matches in test_cases.items():
        matches = list(fuzzyfinder(input_text, collection))
        for expected in expected_matches:
            assert expected in matches, f"Expected '{expected}' to match '{input_text}', got {matches}"


def test_kubernetes_path_fuzzy_matching():
    """Test fuzzy matching with Kubernetes path patterns"""
    # One-segment paths with typos
    namespaces = ['default', 'kube-system', 'monitoring']
    namespace_test_cases = {
        'defult': ['default'],
        'defa': ['default'],
        'dflt': ['default'],
        'kube': ['kube-system'],
        'kbs': ['kube-system'],
        'k-s': ['kube-system'],
        'montring': ['monitoring'],
    }

    for input_text, expected_matches in namespace_test_cases.items():
        matches = list(fuzzyfinder(input_text, namespaces))
        for expected in expected_matches:
            assert expected in matches, f"Expected '{expected}' to match '{input_text}', got {matches}"

    # Resource types with typos
    resource_types = ['pods', 'deployments', 'services', 'configmaps', 'secrets']
    resource_type_test_cases = {
        'pod': ['pods'],
        'pds': ['pods'],
        'deploy': ['deployments'],
        'dploy': ['deployments'],
        'deploymnts': ['deployments'],
        'serv': ['services'],
        'srvcs': ['services'],
        'cfg': ['configmaps'],
        'cfgmps': ['configmaps'],
        'secrt': ['secrets'],
    }

    for input_text, expected_matches in resource_type_test_cases.items():
        matches = list(fuzzyfinder(input_text, resource_types))
        for expected in expected_matches:
            assert expected in matches, f"Expected '{expected}' to match '{input_text}', got {matches}"

    # Resource names with typos
    resource_names = ['nginx', 'postgres', 'redis', 'mongodb', 'python-app']
    resource_name_test_cases = {
        'ngnx': ['nginx'],
        'pstgres': ['postgres'],
        'rds': ['redis'],
        'mngo': ['mongodb'],
        'pythn': ['python-app'],
        'py-app': ['python-app'],
    }

    for input_text, expected_matches in resource_name_test_cases.items():
        matches = list(fuzzyfinder(input_text, resource_names))
        for expected in expected_matches:
            assert expected in matches, f"Expected '{expected}' to match '{input_text}', got {matches}"


def test_path_segment_fuzzy_matching():
    """Test simulating path segment matching for commands like cd"""
    # Test first segment (namespace)
    test_input = "defult"
    namespaces = ['default', 'kube-system', 'monitoring']
    matches = list(fuzzyfinder(test_input, namespaces))
    assert 'default' in matches, f"Expected 'default' to match '{test_input}', got {matches}"

    # Test second segment (resource type)
    test_input = "deploy"
    resource_types = ['pods', 'deployments', 'services', 'configmaps', 'secrets']
    matches = list(fuzzyfinder(test_input, resource_types))
    assert 'deployments' in matches, f"Expected 'deployments' to match '{test_input}', got {matches}"

    # Test third segment (resource name)
    test_input = "ngnx"
    resource_names = ['nginx', 'postgres', 'redis', 'mongodb', 'python-app']
    matches = list(fuzzyfinder(test_input, resource_names))
    assert 'nginx' in matches, f"Expected 'nginx' to match '{test_input}', got {matches}"


def test_complex_multi_segment_fuzzy_input():
    """Test fuzzy matching with complex path patterns"""
    # These tests simulate how the completer would process path segments
    # The real implementation would split these paths and process each segment

    # This test directly tests fuzzyfinder functionality, not the completer itself
    # So we should just focus on testing the fuzzyfinder functionality

    # Define segments for different levels
    namespaces = ['default', 'kube-system', 'monitoring']
    resources_types = {
        'default': ['pods', 'deployments', 'services'],
        'kube-system': ['pods', 'deployments', 'daemonsets'],
        'monitoring': ['pods', 'services', 'configmaps']
    }
    resource_names = {
        'default/pods': ['nginx', 'postgres', 'redis'],
        'default/deployments': ['web', 'api', 'worker'],
        'kube-system/pods': ['coredns', 'kube-proxy', 'metrics-server']
    }

    # Test multi-segment path matching
    # For "defult/deploy"
    namespace_matches = list(fuzzyfinder("defult", namespaces))
    assert 'default' in namespace_matches

    resource_type_matches = list(fuzzyfinder("deploy", resources_types['default']))
    assert 'deployments' in resource_type_matches

    # For "dflt/pods/ngnx"
    namespace_matches = list(fuzzyfinder("dflt", namespaces))
    assert 'default' in namespace_matches

    pod_matches = list(fuzzyfinder("pods", resources_types['default']))
    assert 'pods' in pod_matches

    name_matches = list(fuzzyfinder("ngnx", resource_names['default/pods']))
    assert 'nginx' in name_matches

    # For "k-s/pods/crdns"
    namespace_matches = list(fuzzyfinder("k-s", namespaces))
    assert 'kube-system' in namespace_matches

    pod_matches = list(fuzzyfinder("pods", resources_types['kube-system']))
    assert 'pods' in pod_matches

    name_matches = list(fuzzyfinder("crdns", resource_names['kube-system/pods']))
    assert 'coredns' in name_matches

    # Test with mixed case inputs
    namespace_matches = list(fuzzyfinder("DefULt", namespaces))
    assert 'default' in namespace_matches

    resource_type_matches = list(fuzzyfinder("DePlOyMeNtS", resources_types['default']))
    assert 'deployments' in resource_type_matches

    # Test with more realistic typos (not too severe)
    namespace_matches = list(fuzzyfinder("defalt", namespaces))  # Missing 'u'
    assert 'default' in namespace_matches

    # Note: The fuzzyfinder library has limitations with transposed characters
    # Instead test with characters in correct order but some missing
    pod_matches = list(fuzzyfinder("dploymnts", resources_types['default']))  # Missing some vowels, but characters in order
    assert 'deployments' in pod_matches
