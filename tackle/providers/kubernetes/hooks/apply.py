from kubernetes import client, config, utils

from tackle.models import BaseHook, Field


class K8sApplyHook(BaseHook):
    """Hook for getting current kubeconfig context."""

    hook_type: str = 'k8s_apply'

    yaml_dir: str = Field(...)

    def exec(self):
        config.load_kube_config()
        k8s_client = client.ApiClient()
        utils.create_from_directory(k8s_client, self.yaml_dir, verbose=True)
