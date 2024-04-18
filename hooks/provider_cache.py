import os

from pydantic import BaseModel

from tackle import BaseHook, Field
from tackle.context import Context, Hooks
from tackle.imports import import_python_hooks_from_file


class CachedHook(BaseModel):
    hook_name: str
    module_name: str
    provider_name: str
    hooks_path: str


class GenerateNativeHookCache(BaseHook):
    """
    Hook to generate tackle.lock.json files for all the native providers and thereby make
     startup times much faster.
    """

    hook_name = 'provider_cache_data'
    providers_dir: str = Field(
        None,
        description="Abs path to providers dir.",
    )

    cached_hooks_: list = []

    def get_provider_data(
        self,
        context: Context,
        provider_name: str,
        provider_directory: str,
    ):
        for file in os.scandir(os.path.join(provider_directory, 'hooks')):
            file_base, file_extension = os.path.splitext(file.name)
            if file_extension != '.py':
                continue

            context.hooks = Hooks(private={})

            module_name = provider_name + '.hooks.' + file_base
            import_python_hooks_from_file(
                context=context,
                module_name=module_name,
                file_path=file.path,
            )

            for hook_name, hook in context.hooks.private.items():
                self.cached_hooks_.append(
                    CachedHook(
                        hook_name=hook_name,
                        provider_name=provider_name,
                        module_name=module_name,
                        hooks_path=f'../providers/{provider_name}/hooks',
                    ).__dict__
                )

    def exec(self, context: Context):
        if self.providers_dir is None:
            self.providers_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), '..', 'providers'
            )

        context_hooks = context.hooks  # to be put back later

        for i in os.scandir(self.providers_dir):
            if i.is_dir() and i.name != '__pycache__':
                self.get_provider_data(
                    context=context,
                    provider_directory=i.path,
                    provider_name=i.name,
                )

        context.hooks = context_hooks
        return self.cached_hooks_
