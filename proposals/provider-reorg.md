---
id:
title: Provider Reorg
status: implemented
description: Reorganize the providers into logical groups
issue_num: 252
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Provider Reorg

Reorganize the providers into logical groups

- Proposal Status: [implemented](README.md#status)
- Issue Number: [252](https://github.com/sudoblockio/tackle/issue/252)
- Proposal Doc: [provider-reorg.md](https://github.com/sudoblockio/tackle/blob/main/proposals/provider-reorg.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

## New Provider List

- json
- toml
- yaml
- paths
  - path_exists
  - isdir
  - isfile
  - find_in_parent
  - find_in_child
  - path_join
  - abs_path
  - symlink
- data
  - append
  - list_remove
  - update
  - merge
  - pop
  - keys
- context
  - set
  - get
  - [delete]
  - merge
- strings
  - join
  - split
- random
  - random_hex
  - random_string
- files
  - shred
  - chmod
  - remove
  - move
  - copy
  - create_file
  - file
- environment
  - get_env
  - set_env
  - export
  - unset
- system
  - shell
  - command
- git
  - clone
  - meta
- prompts
  - input
  - select
  - checkbox
  - ...
  - [dropdown]
- console
  - markdown
  - table
  - print
- http
  - http_get
  - http_post
  - http_put
  - http_delete
  - webbrowser
- logic
  - match
  - assert
  - [for]
  - [while]
  - [if]
- generate
  - jinja
  - generate
- tackle
  - debug
  - tackle
  - import
  - block
  - provider_docs


- json
- toml
- yaml
- paths
- data
- context
- strings
- random
- files
- environment
- commands
- git
- prompts
- console
- http
- logic
- generate
- tackle

## New layout

- json
- toml
- yaml
- command
- paths
  - path_exists
  - isdir
  - isfile
  - find_in_parent
  - find_in_child
  - path_join
  - abs_path
  - symlink
- context
  - set
  - get
  - [delete]
# TODO: Change these to operate on keys?
  - merge
  - append
  - list_remove
  - update
  - merge
  - pop
  - keys
- strings
  - join
  - split
  - random_hex
  - random_string
- files
  - shred
  - chmod
  - remove
  - move
  - copy
  - create_file
  - file
- environment
  - get_env
  - set_env
  - export
  - unset
- system
  - shell
  - command
- git
  - clone
  - meta
- prompts
  - input
  - select
  - checkbox
  - ...
  - [dropdown]
- console
  - markdown
  - table
  - print
- http
  - http_get
  - http_post
  - http_put
  - http_delete
  - webbrowser
- logic
  - match
  - assert
  - [for]
  - [while]
  - [if]
- generate
  - jinja
  - generate
- tackle
  - debug
  - tackle
  - import
  - block
  - provider_docs
