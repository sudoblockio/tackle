---
id:
title: Filters / Pipe Operators
status: wip
description: Allow for jinja / bash style filters / pipes
issue_num: 249
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

[//]: # (--end-header--start-body--MODIFY)

```yaml
Hook1<-:
  foo: str
  bar: str  
  args: [foo]

call->: literal baz | Hook1 --bar bazz
```