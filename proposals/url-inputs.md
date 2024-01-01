---
id:
title: URL Inputs
status: wip
description: Accept generic URLs for inputs
issue_num: 263
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

[//]: # (--end-header--start-body--MODIFY)


# URL Inputs

> Status: Not Implemented

At one point `requests` was removed from tackle as a requirement which didn't allow the use of http inputs. This proposal would revert that and allow calling http for both cli / hook inputs.

It would work against:
- Providers
  - Any url to a zip
- Files
  - Any url to a tackle file
    - Would need to have some file type detector (ie yaml vs toml etc)

It would be used in:
- CLI inputs
- Hooks
  - tackle
  - yaml / json / toml
  - Default for starting with http, ie `call->: https://...`
    - This would be a simple get
  - import
    - Would be a faster way of importing a hook
    - Does not get version controlled unless the source had that built in

## Examples

```shell
tackle <some GH raw url>
```