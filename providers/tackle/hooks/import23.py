import os
from typing import Any
from pydantic import BaseModel, Field

from tackle import BaseHook, exceptions
from tackle.imports import import_hooks_from_hooks_directory, import_hooks_from_file
from tackle.utils.vcs import get_repo_source
from tackle.factory import new_source
from tackle.utils.command import unpack_args_kwargs_string


class RepoSource(BaseModel):
    """Repo object."""
    src: str
    version: str = None


class ImportHook(BaseHook):
    """
    Hook for importing external tackle providers. Does not actually execute the
     base tackle in the provider but merely makes the hooks and functions available to
     be used in the context. Takes any type as an argument to build `src` and
     `version` import targets.
    """

    hook_name: str = 'import_3'
    src: Any = Field(..., description="A str/list/dict as above.")
    version: str = Field(None, description="Version of src for remote imports.")
    args: list = ['src']

    def get_dir_or_repo(self, src, version):
        """Check if there is a path that matches input otherwise try as repo."""
        if os.path.exists(src):
            return src
        else:
            return get_repo_source(src, version)

    def new_import_src_from_str(self, provider_str: str):
        args, kwargs, flags = unpack_args_kwargs_string(input_string=provider_str)
        if len(args) != 1:
            raise exceptions.TackleHookImportException(
                "",
                context=self.context)
        if len(kwargs) == 0:
            pass
        elif len(kwargs) > 1:
            # We can only have at most one kwarg -> version
            raise exceptions.TackleHookImportException(
                "",
                context=self.context)
        elif len(kwargs) == 1 and 'version' not in kwargs:
            # The only viable kwarg is version
            raise exceptions.TackleHookImportException(
                "",
                context=self.context)
        if len(flags) == 0:
            pass
        elif len(flags) > 1:
            # We can only have at most one flag -> latest
            raise exceptions.TackleHookImportException(
                "",
                context=self.context)
        elif len(flags) == 1 and 'latest' not in flags:
            # The only viable kwarg is version
            raise exceptions.TackleHookImportException(
                "",
                context=self.context)
        if len(kwargs) == 1 and len(flags) == 1:
            # Can't specify both version and latest
            raise exceptions.TackleHookImportException(
                "",
                context=self.context)

        repo_src = RepoSource(
            src=args[0],
            version="",
        )
        return repo_src


    def import_provider(self, provider_str: str):
        repo_src = self.new_import_src_from_str(provider_str)


    def exec(self) -> None:
        if isinstance(self.src, str):
            # Get the provider path either local or remote.
            provider_path = self.get_dir_or_repo(self.src, self.version)
            import_hooks_from_hooks_directory(
                context=self.context,
                hooks_directory=provider_path,
                provider_name="",
            )

        elif isinstance(self.src, list):
            for i in self.src:
                if isinstance(i, str):
                    # import_hooks_from_file(context=self.context, i)
                    pass
                if isinstance(i, dict):
                    # dict types validated above and transposed through same logic
                    repo_source = RepoSource(**i)

                    import_from_path(
                        self,
                        provider_path=self.get_dir_or_repo(
                            repo_source.src, repo_source.version
                        ),
                    )

        elif isinstance(self.src, dict):
            # Don't even check if path is directory as one would never use a dict here
            repo_source = RepoSource(**self.src)
            provider_dir = get_repo_source(
                repo=repo_source.src,
                repo_version=repo_source.version,
            )
            self.provider_hooks.import_from_path(provider_path=provider_dir)