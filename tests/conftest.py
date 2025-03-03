#!/usr/bin/env python3
"""
Pytest configuration file for K8sh tests
"""
import pytest
from tests.common.test_framework import K8shTestFramework, run_test

# Re-export K8shTestFramework to make it available via tests.conftest
__all__ = ['K8shTestFramework', 'run_test']


@pytest.fixture
def framework():
    """
    Create and return a K8shTestFramework instance.
    This fixture can be used by all test files.
    """
    # Initialize the framework with mock enabled by default
    framework = K8shTestFramework(use_mock=True)

    # Start the shell process
    framework.start_shell()

    # Return the framework instance to the test
    yield framework

    # Cleanup after the test is done
    if framework.process is not None:
        framework.process.terminate()
