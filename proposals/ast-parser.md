---
id: ast-parser
title: AST Upgrade
status: wip
description: Upgrade string parsers to use an AST
issue_num: 172
blockers:
  - context-composition
---
[//]: # (--start-header--DO NOT MODIFY)

# AST Upgrade

Upgrade string parsers to use an AST

- Proposal Status: [wip](README.md#status)
- Issue Number: [172](https://github.com/sudoblockio/tackle/issue/172)
- Proposal Doc: [ast-parser.md](https://github.com/sudoblockio/tackle/blob/main/proposals/ast-parser.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

Current parsing is based on regex which works in most use cases but has become:

1. Very complex - Regex is basically unmaintainable
2. Rigid - Can't use equal signs, just spaces
3. Patched in multiple places where an AST strategy would be better

We currently use regex based parsing in:

tackle/utils/command.py - unpack_args_kwargs_string - Main CLI input string / hook call parser
tackle/parser.py - parse_complex_types - Parses types

Both of these parsers could benefit from a more structured tree based parser vs the current regex hack machine.

### Steps

- [ ] Create working POC for custom parser
- [ ] Replace existing main parser
- [ ] Replace type parser
- [ ] Create custom visitor and replace hack for rendering tool

[//]: # (--end-body--)
