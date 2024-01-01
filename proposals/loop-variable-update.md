---
id: loop-variable-update
title: Loop Variable Update
status: implemented
description: Improve the loop parsing logic to allow declaring variables, ie `i in a_list`.
issue_num: 234
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Loop Variable Update

Improve the loop parsing logic to allow declaring variables, ie `i in a_list`.

- Proposal Status: [implemented](README.md#status)
- Issue Number: [234](https://github.com/sudoblockio/tackle/issue/234)
---
[//]: # (--end-header--start-body--MODIFY)

Currently the loop logic inserts temporary variables `item` and `index` into the context so that they are available for rendering but this results in overlapping variables in embedded loops. What would be better is if we supported inserting the variable as part of the `for` key with `var_name in a_list` and similar semantics. Would require overhauling the parser some custom tokenizer.

## Examples

### Current - Still Supported

```yaml
bars:
  - baz
  - bing
foo:
  ->: print {{item}}
  for: bars  
```

### Future

#### Via Macros

Compact expression pre macro
```yaml
bars:
  - baz
  - bing
foo:
  ->: print {{bar}}
  for: bar in bars  
```

Expanded post macro with new keys
```yaml
bars:
  - baz
  - bing
foo:
  ->: print {{bar}}
  for:
    item: bar
    items:
      ... # Some list or string reference to a list
```

Pros:
- Explicit

Cons:
- Need to build additional interface to support item

#### Regex Parsing

Pseudo Code

```python
def do(for_string: str):
    split_for = for_string.split(' in ')
    if len(split_for) == 2:
        for_var = split_for[0]
        # Put that var in tmp context
        loop_items = split_for[1]
    elif len(split_for) == 1:
        for_var = 'item'
        loop_items = split_for[0]
    else:
        raise
    # Then do normal stuff
```

Pros:
- Easy...

Cons:
- None - Will be replaced later when parser comes in


```yaml
a:
  b: 1
  c: 2
  d: 3

e->: var {{item}} --for k, v in a
e:
  b: 1
  c: 2
  d: 3
```