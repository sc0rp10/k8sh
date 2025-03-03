import os
from typing import cast, Union, Optional

from .client import KubernetesClient
from .mock_client import MockKubernetesClient
from .real_client import RealKubernetesClient

instance: Optional[Union[MockKubernetesClient, RealKubernetesClient]] = None


def get_kubernetes_client() -> KubernetesClient:
    """
    Get a Kubernetes client implementation

    Returns:
        A KubernetesClient implementation
    """
    global instance

    if instance is not None:
        return instance

    # Check if mock is forced via environment variable
    if os.environ.get("K8SH_MOCK") == "1":
        instance = MockKubernetesClient()
    else:
        instance = RealKubernetesClient()

    return cast(KubernetesClient, instance)
