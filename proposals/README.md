# Proposals

[//]: # (DO NOT MODIFY - Generate with `tackle` in this directory)
[//]: # (--start--)

| Title | Status | Description | Blockers |
| --- | --- | --- | --- |
| [Declarative Hook Config]() | Implemented | Allow hooks to have a model_config parameter exposing pydantic config params |  |
| [Peg Parser]() | WIP | Change the parser from regex to PEG |  |
| [Special Args]() | WIP | Reserve some arguments for use with tackle (ie import, freeze, update) |  |
| [Tackle Test Rigging]() | WIP | None |  |
| [Default Hook]() | Implemented | Allow files to have a default hook to be called when no arguments are supplied |  |
| [Reserved Fields]() | WIP | Change the syntax of reserved fields to reduce potential conflicts |  |
| [Hook Methods]() | WIP | Allow creating hooks within hooks that act like methods with parameter inheritance. |  |
| [Provider Reorg]() | Implemented | Reorganize the providers into logical groups |  |
| [Return Hook]() | Implemented | None |  |
| [Hook Alias]() | WIP | Alias hooks so they can be called easier |  |
| [Complex Type Use]() | WIP | Using complex types has issues |  |
| [Test Keys]() | WIP | Create a special `test` key that can run tests next to the code |  |
| [URL Inputs]() | WIP | Accept generic URLs for inputs |  |
| [Hook Instantiation]() | WIP | Open the concept of using methods on instantiated hooks |  |
| [Filters / Pipe Operators]() | WIP | Allow for jinja / bash style filters / pipes |  |
| [Typed Macros]() | WIP | Allow creation of macros from within tackle files |  |
| [Async Hook Calls]() | WIP | Add async functionality to the parser |  |
| [Self Hook]() | WIP | Create a special `self` hook to reference the hook's methods during parsing |  |
| [Native Providers in Individual Repos]() | WIP | Move the majority of the providers to remote locations |  |
| [Structured File Hook Shared Functions]() | Considering | Update all the structured file hooks (ie yaml, json, toml, and ini) to have shared functions. |  |
| [Hook Field Validators]() | Implemented | Validate fields with custom logic similar to pydantic's validation |  |
| [Hooks Dir as Base]() | Implemented | Allow the base of a provider be either a hooks dir or tackle file |  |
| [Return Key]() | WIP | Create a special key for returning the value when parsing |  |
| [Pre / Post Context]() | Implemented | Break up the context into pre and post hook parsing groups of data to allow importing hooks |  |
| [Context Composition]() | Implemented | Changing core context from inheritance based object to composition |  |
| [Pydantic 2.0 Upgrade]() | Implemented | Upgrade to pydantic version 2.0 |  |
| [Hook Field Defaults]() | Implemented | Allow flexible ways to declare hook field defaults |  |
| [Splat Operators]() | Implemented | Allow splat operators to instantiate hooks - ie `a_hook **a_dict` or `a_hook *a_list` | [ast-parser]()<br />[peg-parser]()<br /> |
| [Hook Access Modifiers]() | Implemented | Make hooks either public or private allowing distinction for what is in `tackle <target> help`. |  |
| [Private + Bare `exec` Method (ie `exec<_` / `exec`)]() | WIP | None |  |
| [Complex Types]() | Implemented | Declaring hooks as types |  |
| [Overrides Improvements]() | WIP | Improve how overrides are tracked and applied when parsing files / hooks |  |
| [Path Tracking]() | WIP | Modify how paths are tracked and made available through special variables. |  |
| [Command Arrow]() | WIP | Add macro to easily call commands on different platforms |  |
| [AST Upgrade]() | WIP | Upgrade string parsers to use an AST | [context-composition]()<br /> |
| [Loop Variable Update]() | Implemented | Improve the loop parsing logic to allow declaring variables, ie `i in a_list`. |  |
| [Base Methods as Hooks]() | WIP | Allow base methods to be called directly as hooks |  |
| [Remote Provider Cache]() | WIP | Create a cache for remote providers to minimize network calls to git on ever provider import |  |
| [Method Properties]() | WIP | Methods could have properties which inform their behaviour |  |

[//]: # (--end--)

> Table generated with Tackle
