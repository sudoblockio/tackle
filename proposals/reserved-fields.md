---
id:
title: Reserved Fields
status: wip
description: Change the syntax of reserved fields to reduce potential conflicts
issue_num: 243
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Reserved Fields

Change the syntax of reserved fields to reduce potential conflicts

- Proposal Status: [wip](README.md#status)
- Issue Number: [243](https://github.com/sudoblockio/tackle/issue/243)
---
[//]: # (--end-header--start-body--MODIFY)


## Variable Rules

- Reserved variables
  - Very few that could clash
- Prefix underscore -> private
  - Can't set externally
- Suffix with underscore
  - Don't show up in docs

## Variables

### Reserved

is_public: bool = False
args: list = []
- For mapping args to inputs
kwargs: Union[str, dict] = None
- Only used in requests hook with render by default to upgrade to dict
kwargs: str = None
- This maps additional kwargs to a variable

New
args_seperator_: str = None
- Can be set to a comma or something if you want to break up the args with that to a list

V2 - 1
is_public_: bool = False
args_: list = []
kwargs_: str = None

V2 - 1
_is_public: bool = False
_args_: list = []
_kwargs: str = None

env_: Any = None
- Used in blocks / match hooks where new context is created. Needs to be public
- because it will be mutable within a hook (see match).
skip_output: bool = False
- Fields that should not be rendered by default
_render_exclude_default: set = {
    'input_context',
    'public_context',
    'hook_type',
    'else',
}
_render_exclude: set = {}
_render_by_default: list = []

### Private

Used when rendering docs**
_doc_tags: list = []
- For linking issues in the docs so others can potentially contribute
_issue_numbers: list = []  - TODO: Implement this
- Additional callout sections to be included at the top of the docs
_notes: list = []
- Allow hooks to be sorted in the docs
_docs_order: int = 10  - Arbitrary high number so hooks can be sorted high or low
- Parameterized return type description for docs
_return_description: str = None
- Flag for skipping creating the docs for
_wip: bool = False

```python
from tackle import BaseHook, HookConfig
from pydantic import ConfigDict


class SomeHook(BaseHook):
    hook_name = 'foo'
    bar: str

    model_config = ConfigDict(
        extra='forbid',
    )
    hook_config: HookConfig = HookConfig(
        args=['bar'],
    )
```


```yaml
foo<-:
  bar: str

  Config:


```
