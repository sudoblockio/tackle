import os
from typing import Union

from tackle.models import BaseHook, Field


class FlattenPathHook(BaseHook):
    """Hook for flattening a dictionary into a list of paths."""

    hook_type: str = 'flatten_paths'
    paths: Union[dict, list] = Field(
        ...,
        description="A list or map representing paths to files that should be flattened",
    )
    base_path: str = Field('', description="A base path to prefix in the output.")

    args: list = ['paths']

    def flatten_repo_tree(self, output: list, d, parent_key=''):
        """Flatten a dict to so that keys become nodes in a path."""
        if isinstance(d, dict):
            for k, v in d.items():
                new_key = os.path.join(parent_key, k)
                if isinstance(v, str):
                    output.append(os.path.join(new_key, v))
                else:
                    self.flatten_repo_tree(output, v, new_key)

        elif isinstance(d, list):
            for i in d:
                if isinstance(i, str):
                    output.append(os.path.join(parent_key, i))
                else:
                    self.flatten_repo_tree(output, i, parent_key)

        return output

    def exec(self) -> list:
        output = []
        return self.flatten_repo_tree(output, self.paths, self.base_path)
