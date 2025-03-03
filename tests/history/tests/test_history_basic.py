#!/usr/bin/env python3
"""
Basic tests for the history command
"""
import pytest
from unittest.mock import MagicMock

from prompt_toolkit import PromptSession
from prompt_toolkit.history import History

from command.history import HistoryCommand
from state.state import State
from utils.terminal import disable_colors, enable_colors


@pytest.fixture(autouse=True)
def no_color():
    """Disable colors for all tests"""
    disable_colors()
    yield
    enable_colors()


@pytest.fixture
def history_command():
    """Create a history command instance"""
    return HistoryCommand()


@pytest.fixture
def state():
    """Create a state instance"""
    return State()


def test_history_command_name(history_command):
    """Test that the command name is correct"""
    assert history_command.get_name() == "history"


def test_history_command_help(history_command):
    """Test that the command help text is correct"""
    assert "Display command history" in history_command.get_help()


def test_history_command_usage(history_command):
    """Test that the command usage text is correct"""
    usage = history_command.get_usage()
    assert "Usage: history [n]" in usage
    assert "Display the last n commands from history" in usage


def test_history_command_default(history_command, state, capsys):
    """Test that the command shows the default number of history entries"""
    # Create a mock session and history
    mock_history = MagicMock(spec=History)
    mock_history.get_strings.return_value = ["command1", "command2", "command3", "command4", "command5"]

    mock_session = MagicMock(spec=PromptSession)
    mock_session.history = mock_history

    # Set the mock session in the state
    state.set_prompt_session(mock_session)

    # Execute the command with no arguments (default: 10 entries)
    history_command.execute(state, [])

    # Check the output
    captured = capsys.readouterr()
    assert "command1" in captured.out
    assert "command5" in captured.out


def test_history_command_with_count(history_command, state, capsys):
    """Test that the command shows the specified number of history entries"""
    # Create a mock session and history
    mock_history = MagicMock(spec=History)
    mock_history.get_strings.return_value = ["command1", "command2", "command3", "command4", "command5"]

    mock_session = MagicMock(spec=PromptSession)
    mock_session.history = mock_history

    # Set the mock session in the state
    state.set_prompt_session(mock_session)

    # Execute the command with a specific count
    history_command.execute(state, ["3"])

    # Check the output
    captured = capsys.readouterr()
    assert "command3" in captured.out
    assert "command5" in captured.out
    assert "command1" not in captured.out
    assert "command2" not in captured.out


def test_history_command_no_history(history_command, state, capsys):
    """Test that the command handles the case when no session is available"""
    # Don't set a session in the state
    state.set_prompt_session(None)

    # Execute the command
    history_command.execute(state, [])

    # Check the output
    captured = capsys.readouterr()
    assert "No active session found" in captured.out


def test_history_command_empty_history(history_command, state, capsys):
    """Test that the command handles the case when history is empty"""
    # Create a mock session and history
    mock_history = MagicMock(spec=History)
    mock_history.get_strings.return_value = []

    mock_session = MagicMock(spec=PromptSession)
    mock_session.history = mock_history

    # Set the mock session in the state
    state.set_prompt_session(mock_session)

    # Execute the command
    history_command.execute(state, [])

    # Check the output
    captured = capsys.readouterr()
    assert "No history found" in captured.out


def test_history_command_error(history_command, state, capsys):
    """Test that the command handles errors when reading the history"""
    # Create a mock session and history that raises an exception
    mock_session = MagicMock(spec=PromptSession)
    mock_session.history = MagicMock(spec=History)
    mock_session.history.get_strings.side_effect = Exception("Test error")

    # Set the mock session in the state
    state.set_prompt_session(mock_session)

    # Execute the command
    history_command.execute(state, [])

    # Check the output
    captured = capsys.readouterr()
    assert "Error reading history" in captured.out
