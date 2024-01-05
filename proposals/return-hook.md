---
id:
title: Return Hook
status: implemented
description:
issue_num: 256
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Return Hook

None

- Proposal Status: [implemented](README.md#status)
- Issue Number: [256](https://github.com/sudoblockio/tackle/issue/256)
- Proposal Doc: [return-hook.md](https://github.com/sudoblockio/tackle/blob/main/proposals/return-hook.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

> NOTE: See [return-key](return-key.md) for an additional macro for ergonomics.

Currently when a declarative hook is called with an exec, the entire context is parsed with a special field for returning the appropriate value (`return`) being used to specify what the result is of that parsing.

This proposal would add a hook for being able to escape parsing and return a specific value as the public context.

## Examples

Normal parsing
```yaml
foo: bar
return a key->: return {{foo}}
```

Would result in the value `bar` being returned in the public context.

Similarly with `exec`:
```yaml
<-:
  exec:
    foo: bar
    return a key->: return {{foo}}
    something that: is ignored
```

## Implementation

Context can be set within the hook. Need a way to send kill signal to parsing though since once the context is set, we need to be able to stop the parsing of the next key.

> NOTE: Likely this kill signal approach would also enable a macro like approach for implementing [return-key](return-key.md).

