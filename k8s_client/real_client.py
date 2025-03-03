from typing import List, Optional, cast

import yaml
from kubernetes import client, config

from k8s_client.client import KubernetesClient


class RealKubernetesClient(KubernetesClient):
    """Implementation of KubernetesClient that uses the real Kubernetes API"""

    def __init__(self) -> None:
        """Initialize the Kubernetes client"""
        try:
            # Try to load from kube config file
            config.load_kube_config()
            # Test connection
            v1 = client.CoreV1Api()
            v1.list_namespace()
        except Exception:
            try:
                # Try in-cluster config (for when running inside a pod)
                config.load_incluster_config()
                # Test connection
                v1 = client.CoreV1Api()
                v1.list_namespace()
            except Exception as e:
                raise Exception(f"Could not connect to Kubernetes API: {e}")

    def get_namespaces(self) -> List[str]:
        """Get all namespaces from the Kubernetes API"""
        try:
            v1 = client.CoreV1Api()
            namespaces = v1.list_namespace()
            return [ns.metadata.name for ns in namespaces.items]
        except Exception as e:
            print(f"Error getting namespaces: {e}")
            return []

    def get_resource_types(self) -> List[str]:
        """Get all supported resource types"""
        # These are the resource types we support
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
        try:
            if resource_type == "services":
                v1 = client.CoreV1Api()
                services = v1.list_namespaced_service(namespace)
                return [svc.metadata.name for svc in services.items]

            elif resource_type == "deployments":
                apps_v1 = client.AppsV1Api()
                deployments = apps_v1.list_namespaced_deployment(namespace)
                return [deploy.metadata.name for deploy in deployments.items]

            elif resource_type == "daemonsets":
                apps_v1 = client.AppsV1Api()
                daemonsets = apps_v1.list_namespaced_daemon_set(namespace)
                return [ds.metadata.name for ds in daemonsets.items]

            elif resource_type == "statefulsets":
                apps_v1 = client.AppsV1Api()
                statefulsets = apps_v1.list_namespaced_stateful_set(namespace)
                return [sts.metadata.name for sts in statefulsets.items]

            elif resource_type == "replicasets":
                apps_v1 = client.AppsV1Api()
                replicasets = apps_v1.list_namespaced_replica_set(namespace)
                return [rs.metadata.name for rs in replicasets.items]

            elif resource_type == "configmaps":
                v1 = client.CoreV1Api()
                configmaps = v1.list_namespaced_config_map(namespace)
                return [cm.metadata.name for cm in configmaps.items]

            elif resource_type == "secrets":
                v1 = client.CoreV1Api()
                secrets = v1.list_namespaced_secret(namespace)
                return [secret.metadata.name for secret in secrets.items]

            elif resource_type == "ingresses":
                networking_v1 = client.NetworkingV1Api()
                ingresses = networking_v1.list_namespaced_ingress(namespace)
                return [ing.metadata.name for ing in ingresses.items]

            elif resource_type == "pods":
                v1 = client.CoreV1Api()
                pods = v1.list_namespaced_pod(namespace)
                return [pod.metadata.name for pod in pods.items]

            else:
                return []

        except Exception as e:
            print(f"Error getting {resource_type} in namespace {namespace}: {e}")
            return []

    def get_pods_for_resource(self, namespace: str, resource_type: str, resource_name: str) -> List[str]:
        """Get pods associated with a specific resource"""
        try:
            v1 = client.CoreV1Api()

            # Get all pods in the namespace
            pods = v1.list_namespaced_pod(namespace)

            # Filter pods based on owner references
            resource_pods = []

            for pod in pods.items:
                if pod.metadata.owner_references:
                    for owner in pod.metadata.owner_references:
                        # For deployments, we need to find the ReplicaSet first
                        if resource_type == "deployments":
                            apps_v1 = client.AppsV1Api()
                            replicasets = apps_v1.list_namespaced_replica_set(namespace)

                            for rs in replicasets.items:
                                if rs.metadata.owner_references:
                                    for rs_owner in rs.metadata.owner_references:
                                        if rs_owner.kind.lower() == "deployment" and rs_owner.name == resource_name:
                                            # This ReplicaSet belongs to our deployment
                                            if owner.kind.lower() == "replicaset" and owner.name == rs.metadata.name:
                                                resource_pods.append(pod.metadata.name)

                        # Direct ownership for other resource types
                        elif owner.kind.lower() == resource_type[:-1] and owner.name == resource_name:
                            resource_pods.append(pod.metadata.name)

            return resource_pods

        except Exception as e:
            print(f"Error getting pods for {resource_type}/{resource_name} in namespace {namespace}: {e}")
            return []

    def get_pod_containers(self, namespace: str, pod_name: str) -> List[str]:
        """Get containers in a pod"""
        try:
            v1 = client.CoreV1Api()
            pod = v1.read_namespaced_pod(pod_name, namespace)

            containers = []

            # Add main containers
            if pod.spec.containers:
                containers.extend([container.name for container in pod.spec.containers])

            # Add init containers if any
            if pod.spec.init_containers:
                containers.extend([container.name for container in pod.spec.init_containers])

            return containers

        except Exception as e:
            print(f"Error getting containers for pod {pod_name} in namespace {namespace}: {e}")
            return []

    def is_resource_with_children(self, resource_type: str) -> bool:
        """Check if a resource type can have children (e.g., pods)"""
        # Workload controllers and pods have children
        return resource_type in ["deployments", "statefulsets", "daemonsets", "replicasets", "pods"]

    def get_resource_yaml(self, namespace: str, resource_type: str, resource_name: str) -> Optional[str]:
        """Get YAML definition of a resource"""
        try:
            if resource_type == "services":
                v1 = client.CoreV1Api()
                resource = v1.read_namespaced_service(resource_name, namespace)
            elif resource_type == "deployments":
                apps_v1 = client.AppsV1Api()
                resource = apps_v1.read_namespaced_deployment(resource_name, namespace)
            elif resource_type == "daemonsets":
                apps_v1 = client.AppsV1Api()
                resource = apps_v1.read_namespaced_daemon_set(resource_name, namespace)
            elif resource_type == "statefulsets":
                apps_v1 = client.AppsV1Api()
                resource = apps_v1.read_namespaced_stateful_set(resource_name, namespace)
            elif resource_type == "replicasets":
                apps_v1 = client.AppsV1Api()
                resource = apps_v1.read_namespaced_replica_set(resource_name, namespace)
            elif resource_type == "configmaps":
                v1 = client.CoreV1Api()
                resource = v1.read_namespaced_config_map(resource_name, namespace)
            elif resource_type == "secrets":
                v1 = client.CoreV1Api()
                resource = v1.read_namespaced_secret(resource_name, namespace)
            elif resource_type == "ingresses":
                networking_v1 = client.NetworkingV1Api()
                resource = networking_v1.read_namespaced_ingress(resource_name, namespace)
            elif resource_type == "pods":
                v1 = client.CoreV1Api()
                resource = v1.read_namespaced_pod(resource_name, namespace)
            elif resource_type == "namespace":
                v1 = client.CoreV1Api()
                resource = v1.read_namespace(resource_name)
            else:
                return None

            # Convert to dict and then to YAML
            resource_dict = client.ApiClient().sanitize_for_serialization(resource)

            # Remove status and other non-user-editable fields
            if "status" in resource_dict:
                del resource_dict["status"]

            # Remove other system-managed fields
            if "metadata" in resource_dict:
                metadata = resource_dict["metadata"]
                for field in ["creationTimestamp", "resourceVersion", "selfLink", "uid", "generation", "managedFields"]:
                    if field in metadata:
                        del metadata[field]

            return cast(str, yaml.dump(resource_dict, default_flow_style=False))

        except Exception as e:
            print(f"Error getting YAML for {resource_type}/{resource_name} in namespace {namespace}: {e}")
            return None
