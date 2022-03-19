import os
from ruamel.yaml import YAML
import subprocess

from tackle.models import BaseHook, Field


class K8sCurrentContextHook(BaseHook):
    """Hook for getting current kubeconfig context."""

    hook_type: str = 'k8s_current_context'

    def exec(self) -> str:
        kubeconfig_locations = os.environ.get("KUBECONFIG", None)

        if kubeconfig_locations is None:
            raise Exception("KUBECONFIG not set, exiting...")
        yaml = YAML()
        with open(kubeconfig_locations.split(':')[0]) as f:
            context = yaml.load(f)

        return context['current-context']


class K8sContextListHook(BaseHook):
    """Hook for listing kubeconfig contexts."""

    hook_type: str = 'k8s_context_list'

    def exec(self) -> list:
        kubeconfig_locations = os.environ.get("KUBECONFIG", None)

        if kubeconfig_locations is None:
            raise Exception("KUBECONFIG not set, exiting...")

        output_contexts = []
        yaml = YAML()
        for c in kubeconfig_locations.split(':'):
            with open(c) as f:
                context = yaml.load(f)

            for i in context['contexts']:

                if i['name'] not in output_contexts:
                    output_contexts.append(i['name'])
        return output_contexts


class K8sContextMapHook(BaseHook):
    """Hook for return a map of the kubeconfig context details."""

    hook_type: str = 'k8s_context_map'

    def exec(self) -> dict:
        kubeconfig_locations = os.environ.get("KUBECONFIG", None)

        if kubeconfig_locations is None:
            raise Exception("KUBECONFIG not set, exiting...")

        output_contexts = {}
        yaml = YAML()
        for c in kubeconfig_locations.split(':'):
            with open(c) as f:
                context = yaml.load(f)

            for i in context['contexts']:
                if i['name'] not in output_contexts.keys():
                    output_contexts[i['name']] = context
        return output_contexts


class K8sUseContextHook(BaseHook):
    """Hook for using a kube context."""

    hook_type: str = 'k8s_use_context'
    context: str = Field(..., description="The context to use.")

    def exec(self):
        subprocess.run(
            ["kubectl", "config", "use-context", self.context], stdout=subprocess.PIPE
        )
