---
id:
title: Test Keys
status: wip
description: Create a special `test` key that can run tests next to the code
issue_num: 261
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Test Keys

Create a special `test` key that can run tests next to the code

- Proposal Status: [wip](README.md#status)
- Issue Number: [261](https://github.com/sudoblockio/tackle/issue/261)
---
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