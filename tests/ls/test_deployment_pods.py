#!/usr/bin/env python3
"""
Test for the ls command on a deployment to verify correct pod listing
"""


def test_ls_deployment_pods(framework):
    """Test the ls command on a deployment to verify it correctly lists pods"""
    framework.run_test_commands(["cd default/deployments/example-deployment", "ls"])

    # Check if the output contains deployment entries
    # In the mock data, we have nginx-deployment and web-app
    framework.assert_output_contains(["nginx-deployment", "web-app"])

    # Verify the output format includes the directory indicator 'd'
    framework.assert_output_contains(["d "])
