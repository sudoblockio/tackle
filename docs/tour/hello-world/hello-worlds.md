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

**Locally + Copy / Paste**
You can create a file `hello.yaml` and paste in the following or you can run some of these examples in tackle.

```shell
tackle robcxyz/tackle-hello-world
```

### Single line print

Simply use the [print](https://sudoblockio.github.io/tackle/providers/Console/print/) hook.
```yaml
hw->: print Hello world!
```

Anytime a key is suffixed with an arrow going to the right, it means the key is calling a hook, in this case a print hook.

### Print with variables

Using [jinja templating](https://sudoblockio.github.io/tackle/jinja), the print hook can be called in [three different ways](https://sudoblockio.github.io/tackle/jinja) using a variable.
```yaml
words: Hello world!
expanded:
  ->: print
  objects: "{{words}}"
compact->: print {{words}}
jinja_extension->: "{{ print(words) }}"
# Or combinations of the above
```

> Note that key with arrow without an explicit hook is simply rendered

### Interactive prompts

There are several types of [prompt](https://sudoblockio.github.io/tackle/providers/Prompts/) hooks which can also be used.

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

Hooks can have [loops](https://sudoblockio.github.io/tackle/hook-methods/#loops), [conditionals](https://sudoblockio.github.io/tackle/hook-methods/#conditionals), and [other base methods](https://sudoblockio.github.io/tackle/hook-methods/#methods).
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

Hooks can be [written in python](https://sudoblockio.github.io/tackle/python-hooks/). Simply add your code to a `hooks` directory and the hook will be available to be called from a tackle file.

```python
from tackle import BaseHook


class Greeter(BaseHook):
    hook_name = "greeter"
    target: str
    args: list = ['target']

    def exec(self):
        print(f"Hello {self.target}")
```

### Declarative hooks

Hooks can be [declaratively created](https://sudoblockio.github.io/tackle/declarative-hooks/) with tackle. Arrows going to the left are basically reusable functions / methods.

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

Declarative hooks are strongly typed objects with many [declarative fields](https://sudoblockio.github.io/tackle/declarative-hooks#input-fields).
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

Declarative hooks can have [methods](https://sudoblockio.github.io/tackle/declarative-hooks#methods) that extend the base.

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

Declarative hooks also support [inheritance](https://sudoblockio.github.io/tackle/declarative-hooks#extending-hooks).
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

Which can also be called from the command line.

```shell
tackle hello-world.yaml
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

### Self Documenting Declarative CLIs

Documentation can be embedded into the hooks.

`tackle robcxyz/tackle-hello-world help`
```yaml
<-:
  help: This is the default hook
  target:
    type: str
    description: The thing to say hello to
  exec<-:
    greeting->: select Who to greet? --choices ['world','universe']
    hi->: greeter --target {{greeting}}
  greeting-method<-:
    help: A method that greets
    # ... Greeting options / logic
greeter<-:
  help: A reusable greeter object
  target: str
  exec<-:
    hi->: print Hello {{target}}
```

Which when running `tackle hello.yaml help` produces its own help screen.

```text
usage: tackle hello.yaml [--target]

This is the default hook

options:
    --target [str] The thing to say hello to
methods:
    greeting-method     A method that greets
    greeter     A reusable greeter object
```

> That [will] drive a `help` screen by running `tackle hello-world.yaml --help` -> **Coming soon**
