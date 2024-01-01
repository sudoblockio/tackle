---
id: context-composition
title: Context Composition
status: implemented
description: Changing core context from inheritance based object to composition
issue_num: 230
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Context Composition

Changing core context from inheritance based object to composition

- Proposal Status: [implemented](README.md#status)
- Issue Number: [230](https://github.com/sudoblockio/tackle/issue/230)
---
[//]: # (--end-header--start-body--MODIFY)

This proposal would be for refactoring the core context object from an inheritance to a composition based approach. Would have broad implications across the entire stack. This is some long standing technical debt that needs to be paid at some point.  

## Benefits

- Better understandability
    - Right now it is sort of convoluted what represents what
    - Some unneeded copying of data?
- Less possibility of collision of names with base names
- Easier to track calling files / etc which are right now broken
- Possible to solve the import namespace issue?
  - Able to then mock and could improve load times
- Easier understanding of mutable vs immutable objects
  - What changes where / how to parse certain parts of the context (ie source)

## Current Design

- hooks
  - BaseModel
    - LazyImportHook
    - LazyBaseFunction
- models
  - BaseModel
    - FunctionInput
    - JinjaHook
      - context: BaseContext
    - BaseContext
      - BaseHook(BaseContext, Extension)
        - BaseFunction(BaseHook, FunctionInput)
      - Context

## New Design

- HookDefaultMethods
  - if / else / for ...
- BaseHook(BaseModel, Extension) -> [Need to check if Extension is needed]
    - hook_type
    - context: Context [Need alias]
    - methods: HookDefaultMethods [Need alias]
    - properties: HookProperties [Need alias]
      - is_public: bool = False
      - args: list = []
      - kwargs: Union[str, dict] = None
      - skip_output: bool = False
      - _* -> lots of private properties which will

- PyHookType: Union[BaseHook, LazyPyHook]
- DclHookType: Union[BaseHook, LazyDclHook]
- HookType: Union[PyHookType, DclHookType]
- JinjaHook
  - hook
  - context
- PathContext
  - current
  - calling
  - tackle
- Context
  - source: SourceContext
    - Mutable decomposition of the input string and associated args
  - path: PathContext
  - hooks: HooksContext
    - public: dict[str, HookType]
    - private: dict[str, HookType]
  - data: DataContext
    - input, public, private, temporary, existing, override
  - key_path: list = []
  - key_path_block: list = None
  - global_args: list = None
  - global_kwargs: dict = None
  - global_flags: list = None

### New Layout

#### v1

- models
  - rm all init logic - replace with constructors?
- hooks
- parser
- accessors ?
  - Not enough calls...
  - functions
    - new_context
    - new_source
    - new_hook

#### v2

- cli
- main
- models
- constructors
  - new_context
  - new_source
  - new_hook
- parser

### Hook Properties

```yaml
Hook<-:
  Config:  
```

### Reorg

#### v1

- hooks.py -> imports.py
- hooks.py
  - get_hook
  - enrich_hook
  - create_declarative_hook
  - get_declarative_hooks
  - new_hook
  - evaluate_args
  - create_function_model

- parser.py
  - parse_sub_context
  - parse_hook_execute
    - update_hook_with_kwargs_field
  - evaluate_for
  - parse_hook_loop
  - evaluate_if
  - parse_hook
  - run_hook_at_key_path
  - walk_element
  - update_input_context
  - run_declarative_hook
    - update_hook_with_kwargs_and_flags
  - parse_source_args

#### v2

- main
  - new_context -> accessors.py -> models.py
  - new_hook -> accessors.py -> models.py

#### Validators

Old way of doing things was to assert some element is a dict and then check if keys exist in the dict. New way will be to go from element, assert dict, then constructor to create pydantic objects catching every validation error, then to business logic.  

- declarative hook type
-

### POCs

- BaseModel Config overloading
  - We need to make it additive
  - This is needed because we want to do a major refactor to move all hook private properties into the config object
    - With that we can force all the hooks, declarative or otherwise to have a validated set of config parameters
