# Example Hook Calls

Examples of common hook calls that should allow the majority of actions.  

## Prompts

Prompts are based on wrapping functionality of PyInquirer. The most common things one would want to prompt the user around are basic inputs to fields, selections from a list of selections, and checkbox inputs from a list.

### input

Basic inputs functionality for fields. [Docs]()

#### Tackle File
```yaml
input-minimal->: input
input-compact->: input "What stuff?"
input-expanded:
  ->: input
  message: "What stuff?"
  default: things
```

#### Prompt in CLI  

```text
? input-minimal >>>  
? What stuff?  
? What stuff?  things
```

#### Resulting Context

```yaml
input-minimal: <user input>
input-compact: <user input>
input-expanded: things
```

### select





