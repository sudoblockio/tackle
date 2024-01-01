---
id: async
title: Async Hook Calls
status: wip
description: Add async functionality to the parser
issue_num: 226
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Async Hook Calls

Add async functionality to the parser

- Proposal Status: [wip](README.md#status)
- Issue Number: [226](https://github.com/sudoblockio/tackle/issue/226)
---
[//]: # (--end-header--start-body--MODIFY)

Would be cool to implement async functionality but would need another arrow to define the hook as being awaitable.

```yaml
Greeter<-:
  target: str
  args: ['target']
  exec:
    print->: Hello {{target}}

tasks:
  - =>: Greeter world!
  - =>: Greeter earth!
  - =>: Greeter universe!

call->: await gather **tasks
```

Hooks are built via a partial method on the model which would need to be redefined via some [async partial](https://stackoverflow.com/a/66622677/12642712) wrapper. Would need to move the partial method potentially
