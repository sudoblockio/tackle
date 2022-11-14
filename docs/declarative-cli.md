# Declarative CLI

Tackle files can be turned into a self documenting CLI by wrapping business logic with [declarative hooks](./declarative-hooks.md) which also serve as interfaces to calling other tackle hooks / providers. This document shows the semantics of this pattern.

**Example `tackle.yaml`**

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

Running `tackle help` in the same directory as the file above produces its own help screen.

```text
usage: tackle hello.yaml [--target]

This is the default hook

options:
    --target [str] The thing to say hello to
methods:
    greeting-method     A method that greets
    greeter     A reusable greeter object
```

## Default Hook

When calling a tackle provider without any arguments, the parser first calls the default hook which is a key simply with a left facing as shown below.

```yaml
<-:
  help: This is the default hook
  a_field: str  
  exec<-:
    # Your business logic here
    p->: print {{a_field}}
```

Default hooks when run without the `help` argument may require kwargs, flags. For instance running the above example without any arguments will result in an error such as:

```text
1 validation error for
a_field
  field required (type=value_error.missing)
```

This is because no default value has been given for the field `a_field` and so tackle raises an error for that. Check out [declarative hook, input fields docs](declarative-hooks.md) for further information on the options with creating fields.

### Default Hook Additional Context

In the event that there is some additional context outside of the default hook, it is parsed after the default hook has been executed. For instance given this tackle file:

```yaml
<-:
  help: This is the default hook
  a_field: str  
  exec<-:
    foo->: var {{a_field}}
    # Your business logic here
bar->: {{foo}}
```

When running `tackle example.yaml --a_field baz -pf yaml` the result is:

```yaml
foo: baz
bar: baz
```

Notice how the result of the default hook is made available to be used for rendering the key `bar`.

### Default Hook Methods

Default hooks, like other declarative hooks, can have methods that can be embedded within one another. For given the example from the top, when running `tackle example.yaml greeting-method help`, we get a help screen like this:

[//]: # (TODO: Update this with https://github.com/robcxyz/tackle-box/issues/101)

```text
usage: tackle example.yaml greeting-method

A method that greets
```

> Note: Issue [#101](https://github.com/robcxyz/tackle-box/issues/101) updating this

## Normal Hooks

When running `tackle help`, a help screen is not only produced for the default hook but for any other hooks that exist in the [public hook namespace](declarative-hooks.md#public-vs-private-hooks).

For instance to call the `greeter` hook directly from the command line in the top example, one would call:

```shell
tackle example.yaml greeter --target foo
```

In this case, the outer context is not parsed as in the case of the default hook.

## Importing Hooks

Any hook defined in the `hooks` / `.hooks` directory are made available when calling tackle. So for instance lets say we had the following file in `.hooks/some-hooks.yaml`:

```yaml
public<-:
  help: A public hook
  public: foo
private<_:
  help: A private hook
  private: bar
```

When running `tackle example.yaml help`, we would get the public hook showing in the help screen and the private not. On the same vein, both hooks can be used from within the `example.yaml`.

```yaml
call-public->: public
call-private->: private
```

Results in the following with the command: `tackle example.yaml -pf yaml`

```yaml
call-public:
  stuff: public stuff
call-private:
  things: private things
```

> Future version will also allow you to import hooks from remote locations that along with making python hooks public which are private by default.
