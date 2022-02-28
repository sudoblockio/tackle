import os

from tackle.models import BaseHook, Field


class FlattenPathHook(BaseHook):
    """Hook for flattening a dictionary into a list of paths."""

    hook_type: str = 'flatten_paths'
    paths: dict = Field(
        ...,
        description="A dictionary representing paths to files that should be flattened",
    )
    base_path: str = Field('', description="A base path to prefix in the output.")

    _args: list = ['paths']

    def flatten_repo_tree(self, output: list, d, parent_key=''):
        """Flatten a dict to so that keys become nodes in a path."""
        for k, v in d.items():
            new_key = os.path.join(parent_key, k)
            if isinstance(v, str):
                output.append(os.path.join(new_key, v))
            else:
                self.flatten_repo_tree(output, v, new_key)
        return output

    def execute(self) -> list:
        output = []

        return self.flatten_repo_tree(output, self.paths, self.base_path)
