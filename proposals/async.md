---
id: async
title: Async Hook Calls
status: wip
description: Add async functionality to the parser
issue_num: 226
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

[//]: # (--end-header--start-body--MODIFY)

# Async Hook Calls

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
