---
id: hook-alias
title: Hook Alias
status: wip
description: Alias hooks so they can be called easier
issue_num: 236
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

[//]: # (--end-header--start-body--MODIFY)

Would be nice to be able to define aliases for a hook to make them easier to call. For instance the `listdir` hook could additionally be called with `list_dir` or `dir_list`:

```python
from tackle import BaseHook


class ListDirHook(BaseHook):
    hook_name = 'listdir'

    class Config:
        alias = ['list_dir', 'dir_list']
```
