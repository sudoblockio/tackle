"""GCP hooks."""
import logging
import os
import importlib.machinery

import json
import inspect
from pydantic import BaseModel, Field
from typing import List, Union, get_type_hints

from tackle.models import BaseHook, Context
from tackle.utils.paths import listdir_absolute

logger = logging.getLogger(__name__)


# Source: https://www.geeksforgeeks.org/python-split-camelcase-string-to-individual-strings/
def camel_case_split(str):
    """Split up camel case string."""
    words = [[str[0]]]

    for c in str[1:]:
        if words[-1][-1].islower() and c.isupper():
            words.append(list(c))
        else:
            words[-1].append(c)

    return [''.join(word) for word in words]


def get_hook_title(hook: BaseHook, schema: dict):
    try:
        return hook.Config.title
    except AttributeError:
        return ' '.join(camel_case_split(schema['title'])[:-1])


class HookDocField(BaseModel):
    name: str
    required: str
    hook_type: str
    default: Union[str, dict, bool, list] = ""
    description: str = ""


class HookDoc(BaseModel):
    hook_type: str
    description: str = ""
    properties: List[HookDocField]
    output: str = None


class ProviderDocs(BaseModel):
    name: str = None
    hooks: List[HookDoc] = []
    requirements: list = []


def get_hook_properties(schema: dict) -> List[HookDocField]:
    from tackle.models import HookDict

    # # h = HookDict()
    # x = BaseHook(type='tmp', hook_dict=HookDict()).schema_json()
    basehook_properties = json.loads(
        BaseHook(type='tmp', hook_dict=HookDict()).schema_json()
    )['properties']

    output = []
    for k, v in schema['properties'].items():
        # Bypass any refs
        if "$ref" in v:
            continue

        # Filter out properties with the same schema as a base property
        # If the field has a description, assume that is meant to be in
        # the docs.
        if k in basehook_properties and 'description' not in v:
            if basehook_properties[k] == v:
                continue

        # Type is dealt with elsewhere
        if k == 'type':
            continue

        if 'anyOf' in v:
            type = ", ".join([i['type'] for i in v['anyOf']])
        else:
            type = v['type']

        hook_doc = HookDocField(
            name=k,
            required="X" if 'default' in v else "",
            type=type,
            default=v['default'] if 'default' in v else "",
            description=v['description'] if 'description' in v else "",
        )
        output.append(hook_doc)

    return output


class ProviderDocsHook(BaseHook):
    """Hook building provider docs."""

    hook_type: str = "docs"

    path: str = Field(".", description="The path to the provider.")
    output: str = Field(".", description="The path to output the docs to.")

    provider: str = Field(None, description="The provider name.")
    hooks_dir = Field("hooks", description="Directory hooks are in.")

    _args: list = ['path', 'output_path']

    def __init__(self, **data):
        super().__init__(**data)
        if not self.provider:
            self.provider = os.path.basename(self.path)

    def execute(self):
        """Build the docs."""
        docs = ProviderDocs()

        # TODO: update the docs with provider metadata
        # Instantiate a context
        # context_fields = [i for i, _ in BaseHook().dict().items()] # + [i for i, _ in BaseHook().dict().items()]

        path = os.path.abspath(os.path.join(self.path, self.hooks_dir))
        # Loop through python files
        for f in [i for i in listdir_absolute(path) if i.endswith("py")]:
            # Extract out the objects that are derived from the BaseHook
            loader = importlib.machinery.SourceFileLoader(self.provider, f)
            module_classes = inspect.getmembers(loader.load_module(), inspect.isclass)
            hooks = [
                i[1]
                for i in module_classes
                if issubclass(i[1], BaseHook) and i[1] != BaseHook
            ]

            for h in hooks:
                # Generate the json schema
                schema = json.loads(h.schema_json())

                # Generate the docs object
                hook_doc = HookDoc(
                    properties=get_hook_properties(schema),
                    type=inspect.signature(h).parameters['type'].default,
                    description=schema['description']
                    if 'description' in schema
                    else "",
                    output=get_type_hints(h.execute)['return'].__name__
                    if 'return' in get_type_hints(h.execute)
                    else None,
                )
                docs.hooks.append(hook_doc)

        return docs.dict()
