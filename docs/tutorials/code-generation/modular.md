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
? Who are the license holders Me
? What year to end the license (is perpetual basically so don't fret) 2022
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

[//]: # (TODO: Link to docs when done on kubectl wrapper)
