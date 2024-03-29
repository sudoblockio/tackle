# Tackle File Data Manipulation

The tackle data is the portion of a tackle file that is available to be used for rendering or business logic when parsing. There are four memory spaces for data, public, private, existing, and temporary that are explained in more detail in the [memory management](../memory-management.md) docs. Generally speaking, most users don't need to understand the concept in depth as it should be pretty intuitive for the average user.

This document goes over some strategies on how to maintain / build / and manipulate data in a tackle file.

### Running Examples

To run these examples, it is advised that you print the output to see what the context
is when running a file.

```shell
tackle example-file.yaml -p
```

## Data across files

You can merge data from many files very easily using the `tackle` hook or one of many other hooks that read / write files.

**tackle-1.yaml**
```yaml
stuff: things
another_file->: tackle tackle-2.yaml
```

**tackle-2.yaml**
```yaml
foo->: var stuff
```

**Output**

```yaml
stuff: things
another_file:
  foo: things
```

## Private Variables

Objects declared with an underscore arrow (ie `_>`) indicate the output should be going to private which is data that is not exported but can be used for rendering.

```yaml
private_map_>:
  stuff: things
exported_map->: "{{private_map}}"
private_list_>:
  - stuff
  - things
exported_list->: "{{private_list}}"
```

**Output**

```yaml
exported_map:
  stuff: things
exported_list:
  - stuff
  - things
```

## Filtering to key

These examples show filtering to keys using jinja rendering.

```yaml
a_map:
  key: value

map_with_var->: var a_map.key
map_with_macro->: "{{a_map.key}}"

a_list:
  - stuff
  - things

list_with_var->: var a_list[0]
list_with_macro->: "{{a_list[0]}}"
```

**Output**

```yaml
a_map:
  key: value
map_with_var: value
map_with_macro: value
a_list:
- stuff
- things
list_with_var: stuff
list_with_macro: stuff
```

## Merging up keys

Using the [merge](../hook-methods.md#merge) method, you can bring the output up a level if you are in a map.

```yaml
a_map:
  key: value
  stuff: things
merge a_map->: var a_map --merge
```

**Output**

```yaml
a_map:
  key: value
key: value
stuff: things
```

## Append with merge in for loop in list

When merging in a list from a loop, it will append the output.

```yaml
a_list:
  - stuff
  - things
  - ->: var item --for ['foo','bar']
  - ->: var item --for ['foo','bar'] --merge
```

**Output**

```yaml
a_list:
- stuff
- things
- - foo
  - bar
- bar
- foo
```

## Updating a key

We can update a prior key with the [set hook](../providers/Context/set.md). Notice how this hook is private and would not be exported.

```yaml
path:
  to:
    key: value
update stuff_>: update path/to/key "a value"
```

**Output**

```yaml
path:
  to:
    key: a value
```

## Appending to a List

We can update a prior key with the [set hook](../providers/Context/set.md). Notice how this hook is private and would not be exported.

```yaml
path:
  to:
    a_list:
      - stuff
append things->: append path/to/a_list things
```

**Output**

```yaml
path:
  to:
    a_list:
      - stuff
      - things
```

## Temporary Context

When you are within a block, you are in an indexed memory space where the nearest keys take preference to previously parsed keys.

```yaml
foo: bar
stuff: things
a_block->:
  if: true
  foo: baz
  check foo->: assert {{foo}} baz
  check stuff->: assert {{stuff}} things
check block->: assert {{a_block.foo}} baz
```
