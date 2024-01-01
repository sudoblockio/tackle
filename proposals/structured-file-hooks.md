---
id:
title: Structured File Hook Shared Functions
status: considering
description: Update all the structured file hooks (ie yaml, json, toml, and ini) to have shared functions.
issue_num: 260
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Structured File Hook Shared Functions

Update all the structured file hooks (ie yaml, json, toml, and ini) to have shared functions.

- Proposal Status: [considering](README.md#status)
- Issue Number: [260](https://github.com/sudoblockio/tackle/issue/260)
---
[//]: # (--end-header--start-body--MODIFY)

The yaml, json, toml, and ini share a lot of the same operations and so should have some shared libraries. Right now we have a bloated `*_in_place` hook. In the future it would be good to have a shared library of operations that each tool wraps.

Supported hooks (yaml as example):

- yaml_update_key
- yaml_merge_key
- yaml_remove_key
- yaml_pop_key
- yaml_pop_item
- yaml_insert_item
- yaml_append_item

- yaml_read

#### Comment Preserving

- yaml
  - Should on read and write
- json
  - n/a
- toml
  - Has read but write? - [pep 680](https://peps.python.org/pep-0680/)
- ini
  - [SO Issue](https://stackoverflow.com/a/19432072/12642712)

## New Hooks

- yaml_update
  - fields
    - file
    - Optional - key
    - Value
    - in_place - bool
  - Reads yaml and updates
- yaml_update_in_place

- yaml_append
- yaml_delete
- yaml_pop
- yaml_get

- yaml_parse / yaml_read
  - Already have yamldecode / yamlencode
  - Reads a string into a yaml
  - `yaml` hook by default takes a string to a path. If that is not a path then it should simply throw error and not try to parse as string.

