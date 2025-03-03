#!/usr/bin/env python3
"""
Basic tests for the clear command
"""
import pytest
from unittest.mock import patch

from command.clear import ClearCommand
from state.state import State
from utils.terminal import disable_colors, enable_colors


@pytest.fixture(autouse=True)
def no_color():
    """Disable colors for all tests"""
    disable_colors()
    yield
    enable_colors()


@pytest.fixture
def clear_command():
    """Create a clear command instance"""
    return ClearCommand()


@pytest.fixture
def state():
    """Create a state instance"""
    return State()


def test_clear_command_name(clear_command):
    """Test that the command name is correct"""
    assert clear_command.get_name() == "clear"


def test_clear_command_aliases(clear_command):
    """Test that the command aliases are correct"""
    assert "cls" in clear_command.get_aliases()


def test_clear_command_help(clear_command):
    """Test that the command help text is correct"""
    assert "Clear the terminal screen" in clear_command.get_help()


def test_clear_command_usage(clear_command):
    """Test that the command usage text is correct"""
    usage = clear_command.get_usage()
    assert "Usage:" in usage
    assert "clear" in usage
    assert "cls" in usage


@patch('os.system')
@patch('subprocess.run')
def test_clear_command_execution_unix(mock_run, mock_system, clear_command, state, capsys):
    """Test that the command executes correctly on Unix-like systems"""
    # Mock platform.system to return a Unix-like OS
    with patch('platform.system', return_value='Darwin'):
        clear_command.execute(state, [])

        # Check that the ANSI escape sequence was printed
        captured = capsys.readouterr()
        assert "\033c" in captured.out

        # Check that subprocess.run was called with the clear command
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["clear"]

        # Check that os.system was not called
        mock_system.assert_not_called()


@patch('os.system')
@patch('subprocess.run')
def test_clear_command_execution_windows(mock_run, mock_system, clear_command, state):
    """Test that the command executes correctly on Windows"""
    # Mock platform.system to return Windows
    with patch('platform.system', return_value='Windows'):
        clear_command.execute(state, [])

        # Check that os.system was called with cls
        mock_system.assert_called_once_with("cls")

        # Check that subprocess.run was not called
        mock_run.assert_not_called()


@patch('subprocess.run')
def test_clear_command_fallback(mock_run, clear_command, state, capsys):
    """Test that the command falls back to ANSI escape sequence if subprocess.run fails"""
    # Mock subprocess.run to raise FileNotFoundError
    mock_run.side_effect = FileNotFoundError()

    # Mock platform.system to return a Unix-like OS
    with patch('platform.system', return_value='Linux'):
        clear_command.execute(state, [])

        # Check that the ANSI escape sequence was printed
        captured = capsys.readouterr()
        assert "\033c" in captured.out

        # Check that subprocess.run was called with the clear command
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["clear"]
