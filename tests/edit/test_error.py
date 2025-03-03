#!/usr/bin/env python3
"""
Test for the edit command error cases
"""


# Import the framework fixture
def test_edit_no_args(framework):
    """Test edit command with no arguments"""
    # Run the edit command with no arguments
    framework.run_test_commands([
        "edit"
    ])

    # Assert that an error message was printed
    framework.assert_output_contains([
        "Error: No resource specified"
    ])

# def test_edit_kubectl_not_found(framework):
#     """Test edit command when kubectl is not found"""
#     # Run the edit command
#     framework.run_test_commands([
#         "cd default",
#         "edit nginx-pod"
#     ])

#     # Assert that the correct message was printed (in mock mode)
#     framework.assert_output_contains([
#         "Would run: kubectl edit nginx-pod -n default"
#     ])

# def test_edit_command_failed(framework):
#     """Test edit command when kubectl command fails"""
#     # Run the edit command
#     framework.run_test_commands([
#         "cd default",
#         "edit nginx-pod"
#     ])

#     # Assert that the correct message was printed (in mock mode)
#     framework.assert_output_contains([
#         "Would run: kubectl edit nginx-pod -n default"
#     ])
