import os

from pydantic import (  # noqa
    BaseModel,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
)

from tackle import BaseHook, Context, exceptions
from tackle.factory import new_context
from tackle.imports import import_hooks_from_file
from tackle.utils.command import unpack_args_kwargs_string


class RepoSource(BaseModel):
    """Repo object."""

    src: str
    version: str | None = None
    latest: bool | None = None

    @field_validator('latest')
    def check_both_version_and_latest_defined(cls, v: bool, info: ValidationInfo):
        if info.data['version'] is not None:
            raise ValueError
        return v


class ImportHook(BaseHook):
    """
    Hook for importing external tackle providers. Does not actually execute the
     base tackle in the provider but makes the hooks defined in the hooks directory
     available to be called. Takes any type as an argument to build `src` and
     `version` import targets.
    """

    hook_name = 'import'
    src: str | list = Field(
        ...,
        description="A str reference to a source or a list of dicts with strings that "
        "will be expanded with args (ie `foo --version latest`) or objects "
        "(ie `[src: foo]).",
    )
    version: str = Field(None, description="Version of src for remote imports.")
    latest: bool = Field(None, description="Flag to pull latest version.")

    skip_output: bool = True
    args: list = ['src']

    def _do_import(self, context: 'Context', src: str, version: str, latest: bool):
        if os.path.isfile(src):
            import_hooks_from_file(
                context=context,
                provider_name=os.path.basename(src).replace('-', '_').replace(' ', '_'),
                file_path=src,
            )
        else:
            tmp_context = new_context(
                src,
                checkout=version,
                latest=latest,
                _hooks=context.hooks,
                _strict_source=True,
            )
            # Put the hooks in right namespace
            context.hooks.public.update(tmp_context.hooks.public)
            context.hooks.private.update(tmp_context.hooks.private)

    def _create_repo_source(self, context: Context, **kwargs) -> RepoSource:
        try:
            return RepoSource(**kwargs)
        except ValidationError as e:
            raise exceptions.TackleHookImportException(
                f"Malformed input for `import` hook. \n{e}", context=context
            )
        except ValueError:
            self._raise_when_both_version_and_latest_are_defined(context=context)

    def _raise_when_both_version_and_latest_are_defined(self, context: Context):
        raise exceptions.TackleHookImportException(
            "In the import hook, you can't define both a `version` and `latest` "
            "arguments.",
            context=context,
        )

    def _new_import_src_from_str(self, context: Context, provider_str: str):
        """Unpack the string into src, version, and latest based on flags."""
        # Note: This is kinda dirty but works. Could be cleaned up...
        args, kwargs, flags = unpack_args_kwargs_string(input_string=provider_str)

        output = {}
        if len(args) != 1:
            raise exceptions.TackleHookImportException(
                f"Need to have a src specified in import string=`{provider_str}`",
                context=self.context,
            )
        output['src'] = args[0]

        if len(kwargs) == 0:
            pass
        elif len(kwargs) > 1:
            # We can only have at most one kwarg -> version
            raise exceptions.TackleHookImportException("", context=context)
        elif len(kwargs) == 1 and 'version' not in kwargs:
            # The only viable kwarg is version
            raise exceptions.TackleHookImportException("", context=context)
        else:
            output['version'] = kwargs['version']

        if len(flags) == 0:
            pass
        elif len(flags) > 1:
            # We can only have at most one flag -> latest
            raise exceptions.TackleHookImportException(
                f"Extra flags detected in import string=`{provider_str}`",
                context=context,
            )
        elif len(flags) == 1 and 'latest' not in flags:
            # The only viable flag is `latest`
            raise exceptions.TackleHookImportException(
                f"Unknown flag detected in import string=`{provider_str}`",
                context=context,
            )
        else:
            output['latest'] = True
        return output

    def exec(self, context: 'Context') -> None:
        if isinstance(self.src, str):
            if self.version is not None and self.latest is not None:
                self._raise_when_both_version_and_latest_are_defined(context)
            self._do_import(
                context=context,
                src=self.src,
                version=self.version,
                latest=self.latest,
            )
        elif isinstance(self.src, list):
            for i in self.src:
                if isinstance(i, str):
                    kwargs = self._new_import_src_from_str(context, provider_str=i)
                    repo_source = self._create_repo_source(context=context, **kwargs)
                else:
                    repo_source = self._create_repo_source(context=context, **i)
                self._do_import(
                    context=context,
                    src=repo_source.src,
                    version=repo_source.version,
                    latest=repo_source.latest,
                )
