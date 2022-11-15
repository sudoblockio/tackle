# Modular Code Generation

Code generation can be made modular by calling other code generating tackle providers which can be either remote or local or breaking up how to read in context.

## Using Tackle Providers

One of the main reasons tackle was originally made was to build modular code generators. The vision is that there will be a few, well crafted tackle providers to create different sections of boilerplate which can be easily updated over time. A good example of boilerplate is a license file which this snippet can call.

```yaml
# project_slug is a standard name for your package directory
project_slug->: input What to call the project?
license->: tackle robcxyz/tackle-license --output {{project_slug}}
# project_slug is again used for other rendering outputs
```

Which will prompt you such as below:

```text
? What to call the project? MyApp
❯ Apache 2.0
  MIT
  GPL Version 3
  BSD Version 3
  Closed source
? Who are the license holders? Me
? What year to end the license? 2022
```

This provider can also be called from the command line:

```shell
tackle robcxyz/tackle-license
```

Which also comes with a nice help screen:

```shell
tackle robcxyz/tackle-license help
```

Hopefully over time, providers will be created that specialize in certain files / aspects of code and people can then stitch together templates more easily.

#### Tackle provider versions  

By default, tackle uses the latest github released version unless there is not official release in which case it uses the version in the default branch. Fortunately there is a way to pin the version of an imported tackle with the `checkout` flag which under the hood, is performing a `git checkout` command to get the proper version of the code. For instance:

```yaml
# Use the latest version in the default branch
latest->: tackle robcxyz/tackle-provider --latest
# If the branch was main, the following would be the same
branch->: tackle robcxyz/tackle-provider --checkout main
# Best practice is to pin to some versioned release  
pinned->: tackle robcxyz/tackle-provider --checkout v0.1.0
```

#### Groups of tackle providers

If one wanted to run a number of providers:

```yaml
providers:
  ->: checkbox What additional items do you want to add to the generated code?
  checked: true
  choices:
    - license
    - makefile
    - pre-commit

call providers->: tackle robcxyz/tackle-{{item}} --for providers
```

Since the output of a [`checkbox`](../../providers/Prompts/checkbox.md) is a list, it can be used as the input to the `for` key and since it is a string, it is rendered by default.


## Splitting up Context

Sometimes you want to break up your business logic or build hierarchical ways of merging config files, one could have a pattern such as:

**`child/tackle.yaml`**
```yaml
context: tackle global.yaml --find_in_parent --merge
```

**`global.yaml`**

```yaml
envs_>:
  dev:
    num_servers: 1 # etc...
  prod:
    num_servers: 2

# or in multiple lines / mix
environments:
  - prod
  - dev
env->: select --choices environments
merge it up a level with var hook->: var envs[env] --merge

Or all the above in one line->: var {{envs[select(choices=keys(envs))]}} --merge
```

Resulting in the following context

```yaml
#? env >>> prod
environments:
- prod
- dev
env: prod
num_servers: 2
```

This allows for lots of dev ops related code generation patterns in conjunction with other tools such as kubectl which tackle can wrap.

## Next Tutorials

- [Partial code generation](partial.md)
