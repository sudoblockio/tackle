"""
WARNING: DO NOT MODIFY THIS FILE

Generate it with running

tackle generate-cache
"""
from tackle.models import LazyImportHook

NATIVE_PROVIDERS = {
    {% for h in hooks.private %}'{{hook_name}}': LazyImportHook(
        hook_name="{{hook_name}}",
        hooks_path="{{hooks_path}}",
        mod_name="{{provider_name}}",
        provider_name="{{provider_name}}",
    ),{% end_for %}
}
