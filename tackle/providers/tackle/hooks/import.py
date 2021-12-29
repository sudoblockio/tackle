"""Tackle hooks."""
from typing import Any
from pydantic import BaseModel, Field

from tackle.models import BaseHook
from tackle.utils.vcs import get_repo_source


# """
#     Compact string - This is used as a pre-execution handler
#     ```
#     __import: robcxyz/tackle-demo  # Defaults to default branch (ie main)
#     ```
#
#     ```
#     List of compact strings
#     __import:
#       - robcxyz/tackle-demo
#       - robcxyz/tackle-react-app
#     ```
#
#     List of dicts
#     ```
#     __import:
#       - src: robcxyz/tackle-demo
#         version: main
#       - src: robcxyz/tackle-react-app
#         version: main
#     ```
# """


class RepoSource(BaseModel):
    """Repo object."""

    src: str
    version: str = None


class ImportHook(BaseHook):
    """
    Hook for importing external tackle-box providers. Does not actually execute the
    base tackle in the provider but merely makes the hooks and functions available to
    be used in the context. Takes any type as an argument to to build `src` and
    `version` import targets.

    ### Example

    Expanded strings - Used as a private hook call where key is deleted post exec
    ```
    arbitrary key:
      _>: input
      src: robcxyz/tackle-demo
      version: v0.1.0
    ```
    """

    type: str = 'import'
    src: Any = Field(..., description="A str/list/dict as above.")
    version: str = Field(
        None, description="Version of src for remote imports. Rarely used."
    )
    _args = ['src']

    def execute(self):
        if isinstance(self.src, str):
            # get_repo_source clones and returns path to provider
            provider_dir = get_repo_source(self.src, self.version)
            self.providers_.import_paths([provider_dir])

        elif isinstance(self.src, list):
            provider_dirs = []
            for i in self.src:
                if isinstance(i, str):
                    provider_dirs.append(get_repo_source(repo=i, repo_version=None))
                if isinstance(i, dict):
                    # dict types validated above and transposed through same logic
                    repo_source = RepoSource(**i)
                    provider_dirs.append(
                        get_repo_source(
                            repo=repo_source.src, repo_version=repo_source.version
                        )
                    )

            self.providers_.import_paths(provider_dirs)

        elif isinstance(self.src, dict):
            repo_source = RepoSource(**self.src)
            provider_dir = get_repo_source(
                repo=repo_source.src, repo_version=repo_source.version
            )
            self.providers_.import_paths([provider_dir])
