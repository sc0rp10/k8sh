from typing import List, Dict, Optional, cast

import yaml

from k8s_client.client import KubernetesClient


class MockKubernetesClient(KubernetesClient):
    """Implementation of KubernetesClient that uses mock data"""

    def __init__(self) -> None:
        """Initialize the mock Kubernetes client"""
        print("Using mock Kubernetes client")

        # Mock data for resources
        self.mock_resources: Dict[str, Dict[str, List[str]]] = {
            "default": {
                "deployments": ["nginx-deployment", "web-app"],
                "services": ["kubernetes", "web-service"],
                "configmaps": ["app-config", "system-config"],
                "pods": ["nginx-pod-1", "web-app-pod-1", "web-app-pod-2"],
                "secrets": ["default-token", "app-secrets"],
                "replicasets": ["nginx-rs", "web-app-rs"],
                "daemonsets": ["node-exporter"],
                "statefulsets": ["database"],
                "ingresses": ["web-ingress"],
            },
            "kube-system": {
                "deployments": ["coredns", "metrics-server"],
                "services": ["kube-dns", "metrics-server"],
                "pods": ["coredns-123456", "metrics-server-789012"],
                "configmaps": ["kube-proxy", "kube-dns"],
                "secrets": ["kube-system-token"],
            },
            "kube-public": {
                "configmaps": ["cluster-info"],
            },
        }

        # Mock data for pod containers
        self.mock_pod_containers: Dict[str, List[str]] = {
            "nginx-pod-1": ["nginx", "sidecar"],
            "web-app-pod-1": ["web-app", "logging-agent"],
            "web-app-pod-2": ["web-app", "logging-agent"],
            "coredns-123456": ["coredns"],
            "metrics-server-789012": ["metrics-server"],
        }

        # Mock data for deployment pods
        self.mock_deployment_pods: Dict[str, List[str]] = {
            "nginx-deployment": ["nginx-pod-1"],
            "web-app": ["web-app-pod-1", "web-app-pod-2"],
            "coredns": ["coredns-123456"],
            "metrics-server": ["metrics-server-789012"],
        }

        # Mock data for other controllers
        self.mock_controller_pods: Dict[str, List[str]] = {
            "database": ["database-0", "database-1"],
            "node-exporter": ["node-exporter-node1", "node-exporter-node2"],
        }

    def get_namespaces(self) -> List[str]:
        """Get all namespaces"""
        return list(self.mock_resources.keys())

    def get_resource_types(self) -> List[str]:
        """Get all supported resource types"""
        return [
            "services",
            "deployments",
            "daemonsets",
            "statefulsets",
            "replicasets",
            "configmaps",
            "secrets",
            "ingresses",
            "pods",
        ]

    def get_resources(self, namespace: str, resource_type: str) -> List[str]:
        """Get resources of a specific type in a namespace"""
        if namespace in self.mock_resources and resource_type in self.mock_resources[namespace]:
            return self.mock_resources[namespace][resource_type]
        return []

    def get_pods_for_resource(self, namespace: str, resource_type: str, resource_name: str) -> List[str]:
        """Get pods for a resource"""
        if resource_type == "pods":
            return [resource_name]

        # For simplicity, we'll just return a list with a single pod
        pod_name = f"{resource_name}-pod-1"
        return [pod_name]

    def get_containers_for_pod(self, namespace: str, pod_name: str) -> List[str]:
        """Get containers for a pod"""
        # For simplicity, we'll just return a list with a couple of containers
        if pod_name.endswith("-pod-1"):
            return ["main", "sidecar"]
        else:
            return ["main"]

    def get_pod_containers(self, namespace: str, pod_name: str) -> List[str]:
        """Get containers in a pod"""
        if pod_name in self.mock_pod_containers:
            return self.mock_pod_containers[pod_name]
        return []

    def is_resource_with_children(self, resource_type: str) -> bool:
        """Check if a resource type can have children (e.g., pods)"""
        # Workload controllers and pods have children
        return resource_type in ["deployments", "statefulsets", "daemonsets", "replicasets", "pods"]

    def get_resource_yaml(self, namespace: str, resource_type: str, resource_name: str) -> Optional[str]:
        """Get YAML definition of a resource"""
        # Handle namespace resource
        if resource_type == "namespace" and resource_name in self.get_namespaces():
            resource_dict = {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": resource_name
                }
            }
            return cast(str, yaml.dump(resource_dict, default_flow_style=False))

        # Special handling for pods with complex names (like those generated by deployments)
        if resource_type == "pods" and resource_name not in self.mock_resources.get(namespace, {}).get("pods", []):
            # Check if it's a pod with a deployment-like name pattern
            # For example: nginx-deployment-7f5569bb7f-vsmbx
            for deployment in self.mock_resources.get(namespace, {}).get("deployments", []):
                if resource_name.startswith(f"{deployment}-"):
                    # It's a pod from this deployment, create a mock pod YAML
                    resource_dict = {
                        "apiVersion": "v1",
                        "kind": "Pod",
                        "metadata": {
                            "name": resource_name,
                            "namespace": namespace,
                            "labels": {
                                "app": deployment
                            },
                            "ownerReferences": [{
                                "apiVersion": "apps/v1",
                                "kind": "ReplicaSet",
                                "name": f"{deployment}-7f5569bb7f",
                                "controller": True
                            }]
                        },
                        "spec": {
                            "containers": [{
                                "name": deployment.split("-")[0],
                                "image": f"{deployment.split('-')[0]}:latest"
                            }]
                        }
                    }
                    return cast(str, yaml.dump(resource_dict, default_flow_style=False))

        # Check if resource exists
        if namespace in self.mock_resources and resource_type in self.mock_resources[namespace] and resource_name in self.mock_resources[namespace][resource_type]:

            # Create a mock YAML definition
            resource_dict = {
                "apiVersion": self._get_api_version(resource_type),
                "kind": self._get_kind(resource_type),
                "metadata": {
                    "name": resource_name,
                    "namespace": namespace,
                    "labels": {
                        "app": resource_name
                    }
                }
            }

            # Add resource-specific fields
            if resource_type == "deployments":
                resource_dict["spec"] = {
                    "replicas": 1,
                    "selector": {
                        "matchLabels": {
                            "app": resource_name
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": resource_name
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": "main",
                                    "image": "nginx:latest",
                                    "ports": [
                                        {
                                            "containerPort": 80
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            elif resource_type == "services":
                resource_dict["spec"] = {
                    "selector": {
                        "app": resource_name
                    },
                    "ports": [
                        {
                            "port": 80,
                            "targetPort": 80
                        }
                    ]
                }
                # Special case for kubernetes service
                if resource_name == "kubernetes":
                    resource_dict["spec"] = {
                        "clusterIP": "10.96.0.1",
                        "ports": [
                            {
                                "name": "https",
                                "port": 443,
                                "protocol": "TCP",
                                "targetPort": 443
                            }
                        ]
                    }
            elif resource_type == "configmaps":
                resource_dict["data"] = {
                    "key1": "value1",
                    "key2": "value2"
                }
            elif resource_type == "secrets":
                resource_dict["type"] = "Opaque"
                resource_dict["data"] = {
                    "username": "YWRtaW4=",  # base64 encoded "admin"
                    "password": "cGFzc3dvcmQ="  # base64 encoded "password"
                }
            elif resource_type == "pods":
                resource_dict["spec"] = {
                    "containers": [
                        {
                            "name": "main",
                            "image": "nginx:latest",
                            "ports": [
                                {
                                    "containerPort": 80
                                }
                            ]
                        }
                    ]
                }

                # Add a sidecar container for nginx-pod-1
                if resource_name == "nginx-pod-1":
                    containers = resource_dict["spec"]["containers"]  # type: ignore
                    if isinstance(containers, list):
                        containers.append({
                            "name": "sidecar",
                            "image": "busybox:latest",
                            "command": ["sh", "-c", "while true; do echo sidecar running; sleep 10; done"]
                        })

            # Return YAML representation
            return cast(str, yaml.dump(resource_dict, default_flow_style=False))

        return None

    def _get_api_version(self, resource_type: str) -> str:
        """Get API version for a resource type"""
        api_versions = {
            "pods": "v1",
            "services": "v1",
            "deployments": "apps/v1",
            "daemonsets": "apps/v1",
            "statefulsets": "apps/v1",
            "replicasets": "apps/v1",
            "configmaps": "v1",
            "secrets": "v1",
            "ingresses": "networking.k8s.io/v1",
        }
        return api_versions.get(resource_type, "v1")

    def _get_kind(self, resource_type: str) -> str:
        """Get kind for a resource type"""
        # Convert from plural to singular and capitalize
        if resource_type == "services":
            return "Service"
        elif resource_type == "deployments":
            return "Deployment"
        elif resource_type == "daemonsets":
            return "DaemonSet"
        elif resource_type == "statefulsets":
            return "StatefulSet"
        elif resource_type == "replicasets":
            return "ReplicaSet"
        elif resource_type == "configmaps":
            return "ConfigMap"
        elif resource_type == "secrets":
            return "Secret"
        elif resource_type == "ingresses":
            return "Ingress"
        elif resource_type == "pods":
            return "Pod"
        return resource_type.capitalize()
