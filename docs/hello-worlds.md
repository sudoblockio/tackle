# Hello Worlds!

The following is a collection of hello worlds ranging from simple to contrived that demonstrate the core aspects of writing tackle files.

- [Single line print](#single-line-print)
- [Print with variables](#print-with-variables)
- [Interactive prompts](#interactive-prompts)
- [Loops and conditionals](#loops-and-conditionals)
- [Manipulating context](#manipulating-context)
- [Public vs private hooks](#public-vs-private-hooks)
- [Python hooks](#python-hooks)
- [Declarative hooks](#declarative-hooks)
- [Declarative hook methods](#declarative-hook-methods)
- [Strongly typed declarative hooks](#strongly-typed-declarative-hooks)
- [Declarative hooks inheritance](#declarative-hooks-inheritance)
- [Calling other tackle files](#calling-other-tackle-files)

> Future hello worlds

- Inheriting from schemas like openapi
- Declarative CLI help screens

### Running the `Hello world!` demo

Alternatively, you can run some of these examples in tackle.

```shell
tackle robcxyz/tackle-hello-world
```

### Single line print

Simply use the [print](https://robcxyz.github.io/tackle-box/providers/Console/print/) hook.
```yaml
hw->: print Hello world!
```

### Print with variables

Using [jinja templating](https://robcxyz.github.io/tackle-box/jinja), the print hook can be called in [four different ways](https://robcxyz.github.io/tackle-box/jinja) using a variable.
```yaml
words: Hello world!
expanded:
  ->: print
  objects: "{{words}}"
compact->: print {{words}}
jinja_extension->: "{{ print(words) }}"
jinja_filter->: "{{ words | print }}"
```

> Note that key with arrow without an explicit hook is simply rendered

### Interactive prompts

There are several types of [prompt](https://robcxyz.github.io/tackle-box/providers/Prompts/) hooks which can also be used.

```yaml
name->: input
target:
  ->: select Say hi to who?
  choices:
    - world
    - universe
hello->: print My name is {{name}}. Hello {{target}}!
```

Which looks like this before printing.

```shell
? name >>> Rob
? Say hi to who?
❯ world
  universe
```

### Loops and conditionals

Hooks can have [loops](https://robcxyz.github.io/tackle-box/hook-methods/#loops), [conditionals](https://robcxyz.github.io/tackle-box/hook-methods/#conditionals), and [other base methods](https://robcxyz.github.io/tackle-box/hook-methods/#methods).
```yaml
words:
  - Hello
  - cruel
  - world!
expanded:
  ->: print {{item}}
  for: words
  if: item != 'cruel'
compact->: print {{item}} --for words --if "item != 'cruel'"
```

### Manipulating context

Hooks can manipulate the context with the [context](providers/Context/index.md) provider so using the preceding example, instead of doing a list comprehension we can instead remove the second element using the [pop](providers/Context/pop.md) hook.

```yaml
words:
  - Hello
  - cruel
  - world!
rm cruel->: pop words 1
expanded:
  ->: print {{item}}
  for: words
compact->: print {{item}} --for words
```

### Blocks of context

Sometimes it is convenient to declare a group of logic that contains the [base methods](hook-methods.md) like in this case `for`.

```shell
words:
  - Hello
  - world!
a-block->:
  for: words
  h->: print {{item}} --if "index == 0"
  w->: print {{item}} --if "index == 1"
```

Blocks are simply any key ending with an `->` with a map as the value. In this case we also see that within `for` loops, the iterand is also tracked via the `index` variable.

### Public vs private hooks

Hooks can have both [public and private access modifiers](memory-management.md) which inform whether the hooks value is exported outside of the tackle file / function.

For instance running with the `--print` or `-p` flags, (ie `tackle hello.yaml -p`), only the public context would be exported.

**Input**
```yaml
words_>:
  - Hello
  - world!
output->: var {{item}} --for words
```
**Output**
```yaml
output:
  - Hello
  - world!
```

> You can still use the output of a private hook but only within the tackle file that it is being called. By default, the public context moves with the call between tackle files.

### Python hooks

Hooks can be [written in python](https://robcxyz.github.io/tackle-box/python-hooks/). Simply add your code to a `hooks` directory and the hook will be available to be called from a tackle file.
```python
from tackle import BaseHook

class Greeter(BaseHook):
    hook_type: str = "greeter"
    target: str
    args: list = ['target']
    def exec(self):
        print(f"Hello {self.target}")
```

### Declarative hooks

Hooks can be [declaratively created](https://robcxyz.github.io/tackle-box/declarative-hooks/) with tackle. Arrows going to the left are basically reusable functions / methods.

```yaml
greeter<-:
  target: str
  args: ['target']
  exec<-:
    hi->: print Hello {{target}}
```

Both python and declarative hooks can be called in the same way.
```yaml
hello: world!
compact->: greeter {{hello}}
expanded:
  ->: greeter
  target: "{{hello}}"
jinja_extension->: "{{ greeter(hello) }}"
jinja_filter->: "{{ hello | greeter }}"
```

### Strongly typed declarative hooks

Declarative hooks are strongly typed objects with many [declarative fields](https://robcxyz.github.io/tackle-box/declarative-hooks#input-fields).
```yaml
words<-:
  hi:
    type: str
    regex: ^(Bonjour|Hola|Hello)
  target: str

p->: print {{item}} --for values(words(hi="Hello",target="world!"))
```

Here we are also using the [values](providers/Context/values.md) hook which can also be daisy-chained with the pre-declared `words` hook.

> Note an error would be thrown if the `hi` key did not satisfy the regex.

### Declarative hook methods

Declarative hooks can have [methods](https://robcxyz.github.io/tackle-box/declarative-hooks#methods) that extend the base.

```yaml
words<-:
  hi: Wadup
  say<-:
    target: str
    exec:
      p->: print {{hi}} {{target}}

p->: words.say --hi Hello --target world!
```

### Declarative hooks inheritance

Declarative hooks also support [inheritance](https://robcxyz.github.io/tackle-box/declarative-hooks#extending-hooks).
```yaml
base<-:
  hi:
    default: Hello

words<-:
  extends: base
  say<-:
    target: str
    exec:
      p->: print {{hi}} {{target}}

p->: words.say --target world!
```

### Calling other tackle files

Every hook can be [imported](providers/Tackle/import.md) / [called](providers/Tackle/tackle.md) remotely from github repos with the same options as you would from the command line.

```yaml
import-hello_>: import robcxyz/tackle-hello-world
call->: greeter world!
# Or
local-call->: tackle hello-world.yaml
remote-call->: tackle robcxyz/tackle-hello-world --version v0.1.0
```

## Future work

### Declarative CLIs

Hooks and fields can have documentation embedded in them.

```yaml
greeter<-:
  help: Something that greets
  hi:
    default: Yo
    description: Initial greeting.
  target:
    type: str
    description: Thing to greet.
  exec<-:
    p->: print {{hi}} {{target}}
```

> That [will] drive a `help` screen by running `tackle hello-world.yaml --help` -> **Coming soon**
