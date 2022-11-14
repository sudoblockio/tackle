# Tackle File Context Manipulation

The tackle context is the portion of a tackle file that is available to be used for rendering or business logic when parsing. There are four contexts, public, private, existing, and temporary that are explained in more detail in the [memory management](../memory-management.md) docs. Generally speaking, most users don't need to understand the concept in depth as it should be pretty intuitive for the average user.

This document goes over some strategies on how to maintain / build / and manipulate a context in a tackle file.

### Running Examples

To run these examples, it is advised that you print the output to see what the context
is when running a file.

```shell
tackle example-file.yaml -pf yaml # Can be yaml|toml|json
```

## Basics

## Private Variables

```yaml
private_map_>:
  stuff: things
exported_map->: {{private_map}}
private_list_>:
  - stuff
  - things
exported_list->: {{private_list}}
```

**Resulting context**

```yaml
exported_map:
  stuff: things
exported_list:
  - stuff
  - things
```

## Filtering to Key

- [ ] TODO

## Merging up keys

- [ ] TODO

### Creating Lists

- [ ] TODO

## Changing Keys

- [ ] TODO

## Appending to a List

- [ ] TODO

## Exporting Context

[//]: # (TODO)
