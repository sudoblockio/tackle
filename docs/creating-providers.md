# Providers

This document covers all aspects of creating providers including the semantics of the file structure and dependencies.  For writing hooks which are contained within providers, check out the [writing hooks](writing-hooks.md) document.

As a recap, `providers` are collections of hooks and / or tackle files that call additional hooks. They can be stored remotely in a git repository and then ran / imported from tackle files or called directly from the [command line](command-line.md).  For more information about tackle box's structure, check out the [project structure](project-structure.md) docs.

## Quick Start

Since tackle box is a code generator, it makes sense for it to be able to generate the boilerplate to create providers. The quickest way to do that is with the `tackle-provider` provider which can be run as:

```shell
tackle robcxyz/tackle-provider
```

The provider will then go through a number of configuration options such as:

- What type of license (ie Apache vs MIT vs closed source)
- Types of tests (unittest vs pytest)
- Intention of the provider (code generator vs utility)

Using this provider one can create a functional provider in minutes that when pushed to github can be called with `tackle <your org>/<your repo>`.

## Components



### Requirements

Tackle providers can have their own python requirements.txt allowing python packages to be used within hooks. Requirements can be installed in two ways, by default on import or lazily if one of the hook's is called.  

To install dependencies by default, simply include the `requirements.txt` at the base of the provider and they will be installed on any import error (ie missing some dependency within the hook).

To have dependencies
- [] TODO

