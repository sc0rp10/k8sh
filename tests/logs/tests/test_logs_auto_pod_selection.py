#!/usr/bin/env python3
"""
Tests for the logs command's automatic pod selection feature
"""
import pytest

from command.logs import LogsCommand
from state.state import State
from utils.terminal import disable_colors, enable_colors


@pytest.fixture
def logs_command():
    """Create a logs command instance"""
    disable_colors()
    yield LogsCommand()
    enable_colors()


@pytest.fixture
def state(monkeypatch):
    """Create a mocked state instance with a standard path"""
    state = State()
    monkeypatch.setattr(state, 'get_current_path', lambda: "default")
    return state


def test_logs_command_auto_select_pod(logs_command, state, capsys, monkeypatch):
    """Test that the command automatically selects a pod when path ends with /pods/"""

    # Test with a deployment/pods/ path
    logs_command.execute(state, ["example-deployment/pods/"])
    captured = capsys.readouterr()

    # Should show that it found pods
    assert "Found 3 pods, using pod/example-deployment-7f5569bb7f-vsmbx" in captured.out

    # Should generate the correct kubectl command (note the extra space after 'logs')
    assert "Would run: kubectl logs  --tail 100 -n default example-deployment-7f5569bb7f-vsmbx" in captured.out


def test_logs_command_auto_select_pod_with_namespace(logs_command, state, capsys, monkeypatch):
    """Test that the command handles namespace in the auto pod selection"""

    # Test with a namespace/deployment/pods/ path
    logs_command.execute(state, ["kube-system/example-deployment/pods/"])
    captured = capsys.readouterr()

    # Should show that it found pods
    assert "Found 3 pods, using pod/example-deployment-7f5569bb7f-vsmbx" in captured.out

    # Should generate the correct kubectl command with the specified namespace (note the extra space after 'logs')
    assert "Would run: kubectl logs  --tail 100 -n kube-system example-deployment-7f5569bb7f-vsmbx" in captured.out


def test_logs_command_auto_select_pod_with_flags(logs_command, state, capsys, monkeypatch):
    """Test that the command handles flags with auto pod selection"""

    # Test with flags and a deployment/pods/ path
    logs_command.execute(state, ["-f", "-n", "50", "example-deployment/pods/"])
    captured = capsys.readouterr()

    # Should show that it found pods
    assert "Found 3 pods, using pod/example-deployment-7f5569bb7f-vsmbx" in captured.out

    # Should generate the correct kubectl command with the flags
    assert "Would run: kubectl logs -f --tail 50 -n default example-deployment-7f5569bb7f-vsmbx" in captured.out


def test_logs_command_with_pods_in_middle_of_path(logs_command, state, capsys, monkeypatch):
    """Test that the command doesn't auto-select when /pods/ is in the middle of the path"""

    # Test with a path that has /pods/ in the middle
    logs_command.execute(state, ["example-deployment/pods/some/other/path"])
    captured = capsys.readouterr()

    # Should NOT show that it found pods (no auto-selection)
    assert "Found 3 pods, using pod/" not in captured.out

    # The command should fail with an error message since example-deployment isn't a valid resource type
    assert "Error: Cannot get logs from resource type 'example-deployment'" in captured.out


def test_logs_command_with_full_pod_name_after_pods(logs_command, state, capsys, monkeypatch):
    """Test that the command doesn't auto-select when a full pod name is after /pods/"""

    # Test with a path that has a pod name after /pods/
    logs_command.execute(state, ["example-deployment/pods/example-deployment-7f5569bb7f-vsmbx"])
    captured = capsys.readouterr()

    # Should NOT show that it found pods (no auto-selection)
    assert "Found 3 pods, using pod/" not in captured.out

    # The command should fail with an error message since example-deployment isn't a valid resource type
    assert "Error: Cannot get logs from resource type 'example-deployment'" in captured.out


def test_valid_path_pod_name_in_valid_context(logs_command, state, capsys, monkeypatch):
    """Test a valid path structure where the pod name appears in a pods directory"""

    # Mock a different state with a pods path
    monkeypatch.setattr(state, 'get_current_path', lambda: "default/pods")

    # Test with a specific pod name
    logs_command.execute(state, ["example-deployment-7f5569bb7f-vsmbx"])
    captured = capsys.readouterr()

    # Should NOT trigger the auto-selection feature
    assert "Found 3 pods, using pod/" not in captured.out

    # Should correctly process the pod name directly (no extra space after 'logs' in this case)
    assert "Would run: kubectl logs --tail 100 -n default example-deployment-7f5569bb7f-vsmbx" in captured.out
