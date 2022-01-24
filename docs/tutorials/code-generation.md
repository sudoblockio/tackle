# Code Generation Tutorial

The basic structure of any code generator is to build some kind of context and then render a set of files to a target directory. Most code generators out there have only one way of building the rendering context.  For instance:

- [create-react-app](https://github.com/facebook/create-react-app)
    - All configuration options baked in
- [cookiecutter](https://github.com/cookiecutter/cookiecutter)
    - User inputs based on a json config file
    - tackle-box is a fork of this project
- [openapi-generator](https://github.com/OpenAPITools/openapi-generator)
    - User points to an OpenAPI spec

Tackle-box being more of a DSL allows all these configuration options in a completely modular way with the only catch that you need to explicitly declare all the functionality in a tackle file.  This tutorial walks through how to setup code generators based on each of the above patterns.

## Code Generator Examples

> Coming soon

## Creating Your Own Code Generator

The following sections outline key concepts when creating your own code generator.

### Tackle File Structure

Tackle files are all parsed sequentially such that when you build a code generator, the render context must come before the hook call that generates the code, the [generate hook](../providers/tackle/generate.md). For instance given this file structure:

```
├── templates
│ └── file1.py
│ └── file2.py
└── tackle.yaml
```

With this tackle file:

```yaml
# Arbitrary context
key: value
list:
  - item1
  - item2

# Use the generate hook
generate code:
  ->: generate
  input: templates
  output: src
# Or in compact form
generate code->: generate templates src
```

If it was in a github repo it could then be called in the command line with `tackle <your org>/<your repo>`. The output would be a `src` directory with the templates rendered with jinja based on the preceding context (ie `key` and `list`) in the current working directory.

### Prompting a user for inputs

If one instead wanted to prompt the user for items which would be used to render the templates, one would call various prompt hooks from the `pyinquirer` provider. Some common ones include:

- [input]() - Input strings
- [select]() - List of options where the user can only choose one
- [checkbox]() - Multi select that returns a list
- [confirm]() - Simple confirmation that returns a boolean

For instance:

```yaml
# Arbitrary context
project_slug->: input What is the project's slug (ie head directory)?
license:
  ->: select What license type?
  choices:  
    - Apache
    - MIT

makefile_sections:
  ->: checkbox What utilities to include in makefile?
  choices:
    - build
    - docs
    - tests

ci_enable->: confirm Do you want to setup CI?
generate ci->: generate templates/.github "{{project_slug}}/" --if "{{ci_enable}}"

generate code->: generate templates/src "{{project_slug}}"
```

### Ingesting a spec and transforming it to a render context

> Coming soon - creating OpenAPI transformer hook

### Using other tackle providers  

Code generators are great at setting up boilerplate such as licenses and makefiles but each one shouldn't have to come up with its own license / makefile generator. Tackle box being modular is perfect for this where instead of implementing these items in your code generator, call these items as providers.

For instance if you wanted to include a license, in the tackle file include:

```yaml
license->: tackle robcxyz/tackle-license
```

Which is itself a code generator and will generate the appropriate license and return a map including all the selections and context used to generate the license.

If one alternatively wanted to run a number of providers:

```yaml
providers:
  ->: checkbox What additional items do you want to add to the generated code?
  checked: true
  choices:
    - license
    - makefile
    - bazel

call providers->: tackle robcxyz/tackle-{{item}} --for {{providers}}
```

### Testing code generators

> Coming soon  
