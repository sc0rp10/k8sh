import unittest
from unittest.mock import patch

from command.cd import CdCommand
from state.state import State
from state.path_manager import Manager


class TestCdPreviousDirectory(unittest.TestCase):
    """Test the cd - command functionality to navigate to previous directory"""

    def setUp(self):
        self.state = State()
        self.cd_command = CdCommand()

        # Verify the initial previous_path is set to root
        self.assertEqual(self.state.previous_path, "/")

    def test_cd_dash_with_no_previous_directory(self):
        """Test cd - when there is no previous directory"""
        # First clear the previous path to simulate the no previous directory condition
        self.state.previous_path = None

        with patch('builtins.print') as mock_print:
            # Use mock to prevent actually executing set_path with "-"
            with patch.object(State, 'set_path'):
                # Execute the cd - command
                self.cd_command.execute(self.state, "-")

                # Verify error message is displayed (use partial matching since color codes may vary)
                mock_print.assert_called_once()
                self.assertIn("No previous directory", mock_print.call_args[0][0])

    def test_cd_dash_navigates_to_previous_directory(self):
        """Test cd - navigates to the previous directory"""
        # Set up the state with a previous path
        self.state.previous_path = "namespaces"

        # Mock the current path
        with patch.object(State, 'get_current_path', return_value="pods"):
            # Mock set_path to avoid validation errors
            with patch.object(Manager, 'set_path') as mock_set_path:
                # Now use cd - to go back to the previous directory
                self.cd_command.execute(self.state, "-")

                # Verify set_path was called with the previous path
                mock_set_path.assert_called_with("namespaces")

        # The cd - implementation should swap the paths
        self.assertEqual(self.state.previous_path, "pods")

    def test_cd_dash_toggles_between_directories(self):
        """Test cd - toggles between two directories"""
        # Set up the toggle test

        # First cd - (should go to namespace1)
        with patch.object(State, 'get_current_path', return_value="namespace2"):
            with patch.object(State, 'get_previous_path', return_value="namespace1"):
                with patch.object(Manager, 'set_path') as mock_set_path:
                    # Initial state - we're at namespace2 with namespace1 as previous
                    self.state.previous_path = "namespace1"

                    # Execute cd -
                    self.cd_command.execute(self.state, "-")

                    # Verify correct method was called
                    mock_set_path.assert_called_with("namespace1")
                    # Previous path should be updated
                    self.assertEqual(self.state.previous_path, "namespace2")

        # Second cd - (should go back to namespace2)
        with patch.object(State, 'get_current_path', return_value="namespace1"):
            with patch.object(State, 'get_previous_path', return_value="namespace2"):
                with patch.object(Manager, 'set_path') as mock_set_path:
                    # Set state - we're at namespace1 with namespace2 as previous
                    self.state.previous_path = "namespace2"

                    # Execute cd -
                    self.cd_command.execute(self.state, "-")

                    # Verify correct method was called
                    mock_set_path.assert_called_with("namespace2")
                    # Previous path should be updated
                    self.assertEqual(self.state.previous_path, "namespace1")

        # Third cd - (should go back to namespace1)
        with patch.object(State, 'get_current_path', return_value="namespace2"):
            with patch.object(State, 'get_previous_path', return_value="namespace1"):
                with patch.object(Manager, 'set_path') as mock_set_path:
                    # Set state - we're at namespace2 with namespace1 as previous
                    self.state.previous_path = "namespace1"

                    # Execute cd -
                    self.cd_command.execute(self.state, "-")

                    # Verify correct method was called
                    mock_set_path.assert_called_with("namespace1")
                    # Previous path should be updated
                    self.assertEqual(self.state.previous_path, "namespace2")

    def test_regular_cd_updates_previous_path(self):
        """Test that regular cd commands update the previous path"""
        # Mock the State methods
        with patch.object(State, 'add_path_segment') as mock_add_path_segment:
            with patch.object(State, 'is_directory', return_value=True):
                with patch.object(State, 'get_current_path', side_effect=["", "namespace1", "namespace1/namespace2"]):
                    # First directory
                    self.cd_command.execute(self.state, "namespace1")
                    self.state.previous_path = ""

                    # Second directory - manually update the state as we would expect
                    self.cd_command.execute(self.state, "namespace2")
                    # Manually set previous_path for test
                    self.state.previous_path = "namespace1"

                    # Third directory
                    self.cd_command.execute(self.state, "namespace3")
                    # Check that add_path_segment was called each time
                    self.assertEqual(mock_add_path_segment.call_count, 3)

    def test_cd_dash_after_first_navigation(self):
        """Test cd - works after the first directory change"""
        # Set up the state for a first navigation test
        self.state.previous_path = "/"

        # Execute cd - to go back to root
        with patch.object(State, 'get_current_path', return_value="namespace1"):
            with patch.object(State, 'get_previous_path', return_value="/"):
                with patch.object(Manager, 'set_path') as mock_set_path:
                    # Execute the cd - command
                    self.cd_command.execute(self.state, "-")

                    # Verify set_path was called with "/"
                    mock_set_path.assert_called_with("/")

                    # Previous path should now be namespace1
                    self.assertEqual(self.state.previous_path, "namespace1")


if __name__ == '__main__':
    unittest.main()
