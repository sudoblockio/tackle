---
id:
title: Pre / Post Context
status: implemented
description: Break up the context into pre and post hook parsing groups of data to allow importing hooks
issue_num: 251
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

# Pre / Post Context

Break up the context into pre and post hook parsing groups of data to allow importing hooks

- Proposal Status: [implemented](README.md#status)
- Issue Number: [251](https://github.com/sudoblockio/tackle/issue/251)
- Proposal Doc: [pre-post-context.md](https://github.com/sudoblockio/tackle/blob/main/proposals/pre-post-context.md)

### Overview
[//]: # (--end-header--start-body--MODIFY)

Right now all context outside of a declarative hook call is called after the declarative hook is executed. This sort of goes against how a typical program would be structured where definitions outside of a function are called by means of importing the module. In tackle, it would be nice if the parsing of that context was optional to have called before a function is imported. Since order of the function and the context makes the most sense to inform what context is parsed before the function is called vs after, this proposal suggests breaking up the parsing into these two sections.

Pros:
- Only way to run some kind of import statement before the hooks are called / help is run
- In line with how python scopes variables in a module - variables imported first
- Part of a learning curve that enables more functionality but doesn't get in the way of
- In the future could be updated to include various metaprogramming patterns
  - Dynamically create new functions before import

Cons:
- A little confusing but makes sense

### Examples

```yaml
pre_context_1: bar

<-:
  foo->: {{pre_context_1}}

method_1<-:
  foo->: {{pre_context_2}}

pre_context_2: bar

method_2<-:
  foo->: {{pre_context_1}}

post_context->: {{foo}}
```

Would require rearranging some logic about how the functions are parsed so that on one pass we split up the context between pre_context and post_context for the input context. Not too hard to implement.


### Implementation

Data objects
- input = Mutable object that is parsed
- raw_input = Holds the unparsed data
- pre_input = Data up to the last hook
- post_input = Data after the last hook

```python
def parse_context_2(context: 'Context'):
    """Main entrypoint to parsing a context."""
    # Split the input data so that the pre/post inputs are separated from the hooks
    # TODO: Do on import?
    split_input_data(context=context)
    parse_input(context=context, input=context.data.pre_input)
    parse_input_args_for_hooks(context=context)
    parse_input(context=context, input=context.data.post_input)
```

> Do on import?

Pros:
- Separation of concerns

Cons:
- Splitting and parsing come together so might as well do them together
- Single entrypoint for parsing is more idiomatic
- Splitting document is parsing

Conclusion -> Don't - Do in one function as above
