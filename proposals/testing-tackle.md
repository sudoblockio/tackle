---
id:
title: Tackle Test Rigging
status: wip
description:
issue_num: 262
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Tackle Test Rigging

None

- Proposal Status: [wip](README.md#status)
- Issue Number: [262](https://github.com/sudoblockio/tackle/issue/262)
- Proposal Doc: [testing-tackle.md](https://github.com/sudoblockio/tackle/blob/main/proposals/testing-tackle.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)


## Design

- A make file will exist at the root to
  - Create and activate a venv
  - Install tackle and testing requirements (ie pytest and tox)
- Tackle will then wrap pytest and tox
- Tackle will have two local versions installed
  - A stable version pinned to a working version - `pip install tackle==...`
  - A locally built version from setup.py which will change it's entrypoint to `tkl` based on an environment variable `TACKLE_LOCAL_INSTALL`
- Env var
  - The `TACKLE_LOCAL_INSTALL` env var is set in the make file
  - Naively you can simply use `tackle`, the default entrypoint, but then if you break tackle you can't create the docs / do other stuff that requires tackle
  - This pattern will also be helpful when running tackle locally to maybe inform tackle to recompile the providers

### Dual Installation


## Providers

We will need to make a couple third party providers to

###