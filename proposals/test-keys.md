---
id:
title: Test Keys
status: wip
description: Create a special `test` key that can run tests next to the code
issue_num: 261
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

[//]: # (--end-header--start-body--MODIFY)


```yaml
test<-:
  some: context
  assert->: some=='context'
  assert:
    ->:
      - some=='context'
      - something!='else'
test->:

```