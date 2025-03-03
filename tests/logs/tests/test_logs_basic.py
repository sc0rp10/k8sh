#!/usr/bin/env python3
"""
Basic tests for the logs command
"""
import pytest

from command.logs import LogsCommand
from state.state import State
from utils.terminal import disable_colors, enable_colors


@pytest.fixture(autouse=True)
def no_color():
    """Disable colors for all tests"""
    disable_colors()
    yield
    enable_colors()


@pytest.fixture
def logs_command():
    """Create a logs command instance"""
    return LogsCommand()


@pytest.fixture
def state():
    """Create a state instance"""
    return State()


def test_logs_command_name(logs_command):
    """Test that the command name is correct"""
    assert logs_command.get_name() == "logs"


def test_logs_command_aliases(logs_command):
    """Test that the command aliases are correct"""
    assert "tail" in logs_command.get_aliases()


def test_logs_command_help(logs_command):
    """Test that the command help text is correct"""
    assert "Display logs from a Kubernetes resource" in logs_command.get_help()


def test_logs_command_usage(logs_command):
    """Test that the command usage text is correct"""
    usage = logs_command.get_usage()
    assert "Usage:" in usage
    assert "logs" in usage
    assert "tail" in usage
    assert "-f" in usage
    assert "-n" in usage


def test_logs_command_no_args(logs_command, state, capsys):
    """Test that the command handles no args correctly"""
    logs_command.execute(state, [])
    captured = capsys.readouterr()
    assert "Error: No resource specified" in captured.out


def test_logs_command_invalid_resource_type(logs_command, state, capsys):
    """Test that the command handles invalid resource types correctly"""
    logs_command.execute(state, ["default/services/kubernetes"])
    captured = capsys.readouterr()
    assert "Error: Cannot get logs from resource type 'services'" in captured.out


def test_logs_command_mock_mode(logs_command, state, capsys, monkeypatch):
    """Test that the command works in mock mode"""
    # For simplicity, we'll use absolute paths in the tests
    # This way we don't need to set up the state with a proper path structure

    # Test with a pod
    logs_command.execute(state, ["default/pods/nginx"])
    captured = capsys.readouterr()
    assert "Would run: kubectl logs --tail 100 -n default nginx" in captured.out

    # Test with a container in a pod
    logs_command.execute(state, ["default/pods/nginx/nginx-container"])
    captured = capsys.readouterr()
    assert "Would run: kubectl logs --tail 100 -n default nginx -c nginx-container" in captured.out

    # Test with a deployment
    logs_command.execute(state, ["default/deployments/nginx"])
    captured = capsys.readouterr()
    assert "Would run: kubectl logs --tail 100 -n default deployment/nginx" in captured.out

    # Test with follow flag
    logs_command.execute(state, ["-f", "default/pods/nginx"])
    captured = capsys.readouterr()
    assert "Would run: kubectl logs -f --tail 100 -n default nginx" in captured.out

    # Test with tail lines
    logs_command.execute(state, ["-n", "10", "default/pods/nginx"])
    captured = capsys.readouterr()
    assert "Would run: kubectl logs --tail 10 -n default nginx" in captured.out

    # Test with both flags
    logs_command.execute(state, ["-f", "-n", "50", "/default/pods/nginx"])
    captured = capsys.readouterr()
    assert "Would run: kubectl logs -f --tail 50 -n default nginx" in captured.out
