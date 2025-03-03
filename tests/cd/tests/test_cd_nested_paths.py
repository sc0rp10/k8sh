import pytest
from unittest.mock import patch

from command.cd import CdCommand
from state.state import State
from state.path_manager import Manager


@pytest.fixture
def setup():
    """Setup fixture for cd tests"""
    state = State()
    cd_command = CdCommand()

    # Verify the initial previous_path is set to root
    assert state.previous_path == "/"

    return state, cd_command


def test_cd_dash_workflow(setup):
    """Test the full cd - workflow: simulating real user interaction"""
    state, cd_command = setup

    # This test will focus on the cd - command functionality that allows
    # users to navigate back to their previous directory

    # Instead of directly changing the path manager's private fields,
    # we'll use proper mocking and behavior verification

    # Sequential test of cd - workflow with multiple levels of navigation
    with patch.object(State, 'get_current_path') as mock_get_current_path:
        with patch.object(State, 'get_previous_path') as mock_get_previous_path:
            with patch.object(Manager, 'set_path') as mock_set_path:
                # Reset all mocks to ensure we're starting fresh
                mock_get_current_path.reset_mock()
                mock_get_previous_path.reset_mock()
                mock_set_path.reset_mock()

                # 1. Start with the default state (at root)
                # Initially previous_path is set to root ("/")
                state.previous_path = "/"

                # 2. Test: cd - from default back to root
                # Set up mocks for the first cd - call
                mock_get_current_path.return_value = "default"  # Current path is 'default'
                mock_get_previous_path.return_value = "/"       # Previous path is root

                # Execute cd - command
                cd_command.execute(state, "-")

                # Verify the expected behavior
                mock_set_path.assert_called_with("/")        # Should set path to root
                assert state.previous_path == "default"  # Previous should now be 'default'

                # Reset mocks for the next scenario
                mock_get_current_path.reset_mock()
                mock_get_previous_path.reset_mock()
                mock_set_path.reset_mock()

                # 3. Test: cd - from root back to default/deployments
                # Set up mocks for the second cd - call
                mock_get_current_path.return_value = ""  # Current path is root (empty string)
                mock_get_previous_path.return_value = "default/deployments"  # Previous path is nested

                # Execute cd - command
                cd_command.execute(state, "-")

                # Verify the expected behavior
                mock_set_path.assert_called_with("default/deployments")  # Should set path to nested path
                assert state.previous_path == ""  # Previous should now be root (empty)
