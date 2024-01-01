


```python
from typing import Callable
from tackle import Context

KEY_MACROS: list[Callable[[Context, str], dict]]
VALUE_MACROS: list[Callable[[Context, str], dict]]
```

Macro Types

- key(context: Context, key: str, value: Any) -> (key: str, value: Any)
- value(context: Context, key: str, value: Any) -> (key: str, value: Any)


Macros:

- var_hook_macro(args: list) -> list
  - First arg has
  - value macro

- blocks_macro(context: 'Context')
  - Rewrite a key to a value dict

- compact_hook_call_macro(context: 'Context', element: str) -> dict
  - String values to dict values

- list_to_var_macro(context: 'Context', element: list) -> dict
  - Hooks with keys and list value get turned into var hooks

- function_field_to_parseable_macro(func_dict: dict, context: 'Context', func_name: str) -> dict
  - Takes the fields in a function and updates them based on if they have hooks and things


### Order

Every key:

- Check for arrows in last chars
  - Signifies block / compact / var hooks
  - value is:
    - string
      - compact / var
    - dict
      - block
      -
    - list
      - list to var

### Key Macros

##### Compact Hook

```yaml
key->: value
```

```yaml
key:
  ->: value
```

##### Special Keys

- return
- assert
- import
- merge
- raise
- exit
- print
- cmd
- set
- append
- pop
- delete
- update
- generate
- gen

###### return

```yaml
return->: "{{value}}"
return:
  ->: "{{value}}"
```
```yaml
return: # Key doesn't matter as value is the only data exported
  ->: return
  value: "{{value}}"
```
```yaml
return->:
  "{{value}}": "{{key}}"
return:
  ->:
    "{{value}}": "{{key}}"
```
```yaml
return:
  ->: return
  value:
    "{{value}}": "{{key}}"
```

##### import

```yaml
import->: foo/bar
import:
  ->: foo/bar
```
```yaml
import->:
  - foo/bar
  - foo/bar2
```
```yaml
import:
  ->: import
  providers:
    - foo/bar
```

##### assert

```yaml
assert->: foo==bar
assert:
  ->: foo==bar
```
```yaml
assert->:
  - foo==bar
  - foo==bar2
```
```yaml
assert:
  ->: assert
  skip_output: true
  providers:
    - foo==bar
```

##### merge

```yaml
merge->:
  foo: bar
merge:
  ->: literal  
  ->: var
  merge: true
  input:
    foo: bar
```

##### Expand Keys

```yaml
key:
  ->: value --a-key foo
```

```yaml
key:
  ->: value
  a_key: foo
```

##### Block

```yaml
key:
  ->:
    if: foo == 'bar'
    key: value  
```

```yaml
key:
  ->: block
  if: foo == 'bar'
  key: value  
```

> Note: Block hook maps unknown kwargs to `items`.

Macro could alternatively do this:

```yaml
key:
  ->: block
  if: foo == 'bar'
  items:
    key: value  
```


### Issues

- input_dict
  - Old macros didn't only just return a new value but would re-write the input
  - This is because later in the parsing we use the input dict to grab some data
    - parse_sub_context from new_hook from ...
      - If you don't rewrite the input data then you can't access
      - This call can likely be avoided as I am not sure wtf is happening there
      - Looks like we can grab the new context to parse from


