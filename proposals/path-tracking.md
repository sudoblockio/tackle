---
id: path-tracking
title: Path Tracking
status: wip
description: Modify how paths are tracked and made available through special variables.
issue_num: 244
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Path Tracking

Modify how paths are tracked and made available through special variables.

- Proposal Status: [wip](README.md#status)
- Issue Number: [244](https://github.com/sudoblockio/tackle/issue/244)
---
[//]: # (--end-header--start-body--MODIFY)

There is some ambiguity about what the current directory is. Current logic is

- If remote, current dir is in providers dir
- If another dir, same thing but in that dir

Right now it is not clear what the current path / calling path actually is. This proposal will fix that.

## Solution

Plan is to create a new path object and which stores all the path related data.

Variables:

- current path
  - The current path of the call. Can change based on `chdir`
- calling path
  - The path where tackle was originally called from
- tackle path
  - The path of the tackle provider being used.
  - base / hooks_dir / tackle_file

#### Schema

- Context
  - path:
    - current
      - directory
      - file
    - calling
      - directory
      - file
    - tackle
      - directory
      - hooks_dir
      - file

### Situations

- Call from dir, tackle file in parent, call to remote tackle file, use generate hook
  - current_path = calling_path = cwd
  - tackle_file = the providers dir based on xdg
  - tackle_hook_path = the base dir, wherever the hook was defined, either tackle file or .hooks dir
  - generate hook attempts imports of templates from tackle_file_path and outputs by default in the current_path
- Call from dir, tackle file in parent, call to remote tackle file, use a declarative hook, use generate hook  
  - same as above

Point is we have 2 situations,
1. When calling a local file / provider in the current or parent directory
- For those situations we have the current and calling paths
2. When calling a remote provider
- For that we have calling = current and tackle path for discriminating
