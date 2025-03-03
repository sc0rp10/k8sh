#!/usr/bin/env python3
"""
Test cases for the exec command
"""


def test_exec_deployment(framework):
    """Test exec command on a deployment"""
    # Run the exec command on a deployment
    framework.run_test_commands([
        "exec /default/deployments/nginx-deployment"
    ])

    # Assert that the correct message was printed
    framework.assert_output_contains([
        "Would run: kubectl exec -it -n default deployment/nginx-deployment -- bash"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error:"
    ])


def test_exec_pod(framework):
    """Test exec command on a pod"""
    # Run the exec command on a pod
    framework.run_test_commands([
        "exec /default/pods/nginx-pod-1"
    ])

    # Assert that the correct message was printed
    framework.assert_output_contains([
        "Would run: kubectl exec -it -n default nginx-pod-1 -- bash"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error:"
    ])


def test_exec_deployment_pod(framework):
    """Test exec command on a pod within a deployment"""
    # Run the exec command on a pod within a deployment
    framework.run_test_commands([
        "exec /default/deployments/nginx-deployment/pods/nginx-deployment-12345"
    ])

    # Assert that the correct message was printed
    framework.assert_output_contains([
        "Would run: kubectl exec -it -n default nginx-deployment-12345 -- bash"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error:"
    ])


def test_exec_container(framework):
    """Test exec command on a container within a pod"""
    # Run the exec command on a container within a pod
    framework.run_test_commands([
        "exec /default/pods/nginx-pod-1/nginx"
    ])

    # Assert that the correct message was printed
    framework.assert_output_contains([
        "Would run: kubectl exec -it -n default nginx-pod-1 -c nginx -- bash"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error:"
    ])


def test_exec_deployment_container(framework):
    """Test exec command on a container within a pod within a deployment"""
    # Run the exec command on a container within a pod within a deployment
    framework.run_test_commands([
        "exec /default/deployments/nginx-deployment/pods/nginx-deployment-12345/nginx"
    ])

    # Assert that the correct message was printed
    framework.assert_output_contains([
        "Would run: kubectl exec -it -n default nginx-deployment-12345 -c nginx -- bash"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error:"
    ])


def test_exec_custom_command(framework):
    """Test exec command with a custom command"""
    # Run the exec command with a custom command
    framework.run_test_commands([
        "exec /default/pods/nginx-pod-1 -- sh"
    ])

    # Assert that the correct message was printed
    framework.assert_output_contains([
        "Would run: kubectl exec -it -n default nginx-pod-1 -- sh"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error:"
    ])


def test_exec_relative_path(framework):
    """Test exec command with a relative path"""
    # Run the exec command with a relative path
    framework.run_test_commands([
        "cd /default/pods",
        "exec nginx-pod-1"
    ])

    # Assert that the correct message was printed
    framework.assert_output_contains([
        "Would run: kubectl exec -it -n default nginx-pod-1 -- bash"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error:"
    ])


def test_exec_ssh_alias(framework):
    """Test ssh alias for exec command"""
    # Run the ssh command (which is an alias for exec)
    framework.run_test_commands([
        "ssh /default/pods/nginx-pod-1"
    ])

    # Assert that the correct message was printed
    framework.assert_output_contains([
        "Would run: kubectl exec -it -n default nginx-pod-1 -- bash"
    ])

    # Assert that no error message was printed
    framework.assert_output_not_contains([
        "Error:"
    ])
