# Code Generation Tutorial

The basic structure of any code scaffolding tool is to build some kind of context / map of key value pairs and then render a set of files to a target directory. Tackle box uses jinja syntax internally to build flow control but also ships with a number of hooks to create files and render templates. This document aims to go over the common practices for generating code with tackle box.

## The `generate` Hook

When rendering files, you will want to use the [`generate`](../../providers/Generate/generate.md) hook which can render individual files or directories of templates to some output path. Basically every code generator uses this hook. There are several parameters that can be used with this hook but the simplest way of using it is as a [compact hook](../../writing-tackle-files.md#hook-call-forms) with the first positional value being the path to your templates and the second being the output path. For instance:

```yaml
# Render context
foo: bar

# Call generate hook
generate hook in compact form->: generate path/to/templates output/path
# Or
generate hook in expanded form:
  ->: generate
  templates: path/to/templates
  output: output/path
```

Throughout this tutorial we'll be using it but just know this hook generally comes at the end of your tackle file once you have established a render context (foo=bar in the example above).

## Simplest Example

Most project scaffolding tools work off the general principle of building a render context which is then used to generate code from templates. This render context is typically a map of key value pairs that map the variables in the template to the render context.

For instance if our template was:

**`file.py.tpl`**
```python
def do_thing():
  print("{{words}}")
```

We'd need to have some variable `words` to fill into the template. In tackle, this context is built within the tackle file before one renders files. For instance given the following tackle file:

**`tackle.yaml`**
```yaml
words: Hello world!
gen->: generate file.py.tpl file.py
```

When called by running `tackle` in the same directory would generate a `file.py` with the `words` variable populated.

## Example with Prompting

Similar to cookiecutter, tackle offers the ability to prompt a user for inputs which are then used to render out the files. There are many kinds of [prompt hooks](../../providers/Prompts/index.md) with the most common being the [input](../../providers/Prompts/input.md) prompt (string inputs) and the [select](../../providers/Prompts/select.md) prompt (choices of values) corresponding to cookiecutter's string and [list](https://cookiecutter.readthedocs.io/en/latest/advanced/choice_variables.html) values. Each of these have their first positional argument as a displayed question but this is not required.

For instance given this file structure:

```
├── templates
│ └── file1.py
│ └── file2.py
└── tackle.yaml
```

**`tackle.yaml`**
```yaml
project_name->: input
project_slug->: input --default "{{project_name.lower()|replace(' ', '_')|replace('-', '_')|replace('.', '_')|trim()}}"
github_username->: input What is your Github username / org?
license->: select --choices ['apache','mit']
postgres_version:
  ->: select
  choices:
    - 14
    - 13
    - 12
gen code->: generate templates {{project_slug}}
```

After running `tackle` in the same directory one would be prompted with:

```
? project_name >>> tackle-foo-bar
? project_slug >>> tackle_foo_bar
? What is your Github username / org? robcxyz
? license >>> apache
? postgres_version >>>
  14
❯ 13
  12
```

Before generating the code.

#### Conditional Options

Most project scaffolding is not a "one size fits all" situation such that the template should prompt the user for high level questions and the conditionally prompt a user for additional questions based on the answers of the prior ones. For instance if you had the question "Do you want to use docker?", one could then conditionally expose a subset of options such as "What docker base image do you want to start with?".  For simple conditions, tackle has the [confirm](../../providers/Prompts/confirm.md) hook that prompts the user and outputs a boolean to inform conditionals / blocks that expose a subset of options. Thus, to express some conditionality around creating a Dockerfile, one could have the following:

```yaml
use_docker->: confirm Do you want to use docker?
docker_os->: select What docker base image? --if use_docker --choices ['ubuntu','alpine']
# Or in expanded form
docker_os:
  ->: select What docker base image?
  if: use_docker
  choices:
    - ubuntu
    - alpine
...
gen code->: generate input output
```

Which could then expose a subset of options. If you wanted to express the above in one line, you could also do:

```yaml
docker_os->: select --choices ['ubuntu','alpine','centos'] --if "confirm('Use docker?')"
```

But in this case you would not have the `use_docker` boolean variable which could be useful if building a template.

#### Conditional Blocks

If you are building a decision tree, you might want to consider using [block](../../writing-tackle-files.md#blocks) hooks which allow having a group of hooks being called based on a single condition without having to repeat a bunch of conditionals. For instance given the above docker example, if you wanted to have a number of options:

```yaml
use_docker->: confirm Do you want to use docker?
docker->:
  if: use_docker
  os:
    ->: select What docker base image?
    choices:
      - ubuntu
      - alpine
      - centos
  registry->: select Where to push docker image? --choices ['dockerhub','quay']
  generate dockerfile->: generate templates/Dockerfile {{project_slug}}/Dockerfile

# Use items inside block to render other templates
# For instance one could use {{docker.registry}} in a template
generate ci->: generate templates/.github {{project_slug}}
```

#### Match Hook

> Note: Checkout the [`match`](../../providers/Logic/match.md) hook for creating other types of decision trees.



## Next Tutorials

-


### Using other tackle providers  

Code generators are great at setting up boilerplate such as licenses and makefiles but each one shouldn't have to come up with its own license / makefile generator. Tackle box being modular is perfect for this where instead of implementing these items in your code generator, call these items as providers.

For instance if you wanted to include a license, in the tackle file include:

```yaml
project_slug->: input   # This is the convention for naming the project's head directory
license expanded:
  ->: tackle robcxyz/tackle-license
  context:
    output: {{project_slug}}

# Or in a more compact form
license expanded->: tackle robcxyz/tackle-license --output {{project_slug}}
```

Which is itself a code generator and will generate the appropriate license and return a map including all the selections and context used to generate the license.

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

#### Note on context

Tackle has a memory management system which allows one to pass context from one tackle-file to another. In the above example calling the [license]() provider, one could have written it like:

```yaml
output->: input   # This is the convention for naming the project's head directory
license->: tackle robcxyz/tackle-license
```

This is because the `output` key will be passed into the calling of the `tackle-license` provider.  

### Testing code generators

Once you generate code, it is often helpful to then run the tests within that generated code to make sure it works. For examples on how to do this, checkout the [tackle-provider](https://github.com/robcxyz/tackle-provider) provider which generates the scaffolding to run a provider.

In that provider you will see a [test](https://github.com/robcxyz/tackle-provider/blob/main/tests/test_this.py) which uses a number of fixtures from the [conftest.py](https://github.com/robcxyz/tackle-provider/blob/main/tests/conftest.py) which can be used to run the tests in the generated code.
