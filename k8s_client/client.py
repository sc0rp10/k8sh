from abc import ABC, abstractmethod
from typing import List, Optional


class KubernetesClient(ABC):
    """Abstract base class for Kubernetes client implementations"""

    @abstractmethod
    def get_namespaces(self) -> List[str]:
        """Get all namespaces"""
        pass

    @abstractmethod
    def get_resource_types(self) -> List[str]:
        """Get all supported resource types"""
        pass

    @abstractmethod
    def get_resources(self, namespace: str, resource_type: str) -> List[str]:
        """Get resources of a specific type in a namespace"""
        pass

    @abstractmethod
    def get_pods_for_resource(self, namespace: str, resource_type: str, resource_name: str) -> List[str]:
        """Get pods associated with a specific resource"""
        pass

    @abstractmethod
    def get_pod_containers(self, namespace: str, pod_name: str) -> List[str]:
        """Get containers in a pod"""
        pass

    @abstractmethod
    def is_resource_with_children(self, resource_type: str) -> bool:
        """Check if a resource type can have children (e.g., pods)"""
        pass

    @abstractmethod
    def get_resource_yaml(self, namespace: str, resource_type: str, resource_name: str) -> Optional[str]:
        """Get YAML definition of a resource"""
        pass
