# Proposals

[//]: # (DO NOT MODIFY - Generate with `tackle` in this directory)
[//]: # (--start--)

| Name | Status | Description | Blockers | Related To |
| --- | --- | --- | --- | --- |
| AST Upgrade | WIP | - |  | [] |
| Abbreviate Kwargs | WIP | Allow kwarg flags to be shortened / abbreviated - ie `foo --bar baz` to `foo -b baz` | ast-parser<br />peg-parser<br /> | [] |
| Allow hooks to be called in fields | WIP | Right now you can call hooks from rendering fields but would be great to use an arrow notation as well. |  | [] |
| Command Arrow | Considering | Add a new arrow to indicate calling a command. |  | [] |
| Complex Types | Implemented | Allow complex types including hook types |  | [] |
| Context Composition | WIP | Upgrade the main context object from inheritance to a composition based model. |  | [] |
| Declarative hook config parameters | WIP | Expose config parameters for pydantic's BaseModel to declarative hooks. |  | [] |
| Default Methods as a Hook | Considering | Allow setting literal values if the first arg is |  | None |
| Default hook | Implemented | When running a tackle file, it can help to have a default hook to run. |  | [] |
| Default hook methods | Considering | None |  | [] |
| Hook Access Modifiers | Implemented | Make hooks either public or private allowing distinction for what is in `tackle <target> help`. |  | [] |
| Hook Defaults | Implemented | Declarative hook default values should be parsed for hook calls. |  | [] |
| Hook Directory as the Base Directory | Accepted | This proposal would make the tackle file optional allowing the hooks directory to act alone. |  | [] |
| Hook Methods | Implemented | Allow creating hooks within hooks that act like methods with parameter inheritance. |  | [] |
| Improve Loop Parser | WIP | Improve the loop parsing logic to allow declaring variables, ie `for: i in a_list`.
 |  | ['peg-parser'] |
| Overrides Improvements | WIP | Improve how overrides are tracked and applied when parsing files / hooks |  | [] |
| PEG Parser | WIP | Update the current regex based parser to a PEG parser. |  | [] |
| Partial Generation | Deferred | Generate / update parts of files instead of the whole file |  | [] |
| Path Tracking Improvements | WIP | Modify how paths are tracked and made available through special variables. |  | [] |
| Pydantic v2.0 Upgrade | WIP | Upgrade to pydantic version 2.0 |  | [] |
| Remote Providers | WIP | Move the majority of the providers to remote locations |  | [] |
| Reorganize the Providers | Implemented | Reorganize the providers into more logical groups. |  | [] |
| Splat Operators | WIP | Allow splat operators to instantiate hooks - ie `a_hook **a_dict` or `a_hook *a_list` | ast-parser<br />peg-parser<br /> | [] |
| Structured File Hook Shared Functions | Considering | Update all the structured file hooks (ie yaml, json, toml, and ini) to have shared functions. |  | [] |
| URL Input Strings | Considering | Allow URLs to be input into tackle directly and make requests a dependency. |  | [] |

[//]: # (--end--)


### Status

Implemented
Accepted
WIP
Rejected
Deferred
Abandoned

## Not implemented

In GH issue

