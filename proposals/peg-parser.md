---
id:
title: Peg Parser
status: wip
description: Change the parser from regex to PEG
issue_num: 246
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Peg Parser

Change the parser from regex to PEG

- Proposal Status: [wip](README.md#status)
- Issue Number: [246](https://github.com/sudoblockio/tackle/issue/246)
- Proposal Doc: [peg-parser.md](https://github.com/sudoblockio/tackle/blob/main/proposals/peg-parser.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

The parser isn't very good now and should be overhauled. This was always the plan but the current regex based approach was sufficient to continue at the time.  

This will enable:

- Better [command capabilities](./command-arrow.md)

## Packages

- [parsimonious](https://github.com/erikrose/parsimonious )
- [pegen](https://github.com/we-like-parsers/pegen)
  - Official parser
  - Generates parser which can be used to build AST

## AST Differences

- Allow for a potential
