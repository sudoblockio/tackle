# Providers

This document covers all aspects of creating providers including the semantics of the file structure and dependencies.  For writing hooks which are contained within providers, check out the [writing hooks](writing-hooks.md) document.

As a recap, `providers` are collections of hooks and / or tackle files that call additional hooks. They can be stored remotely in a git repository and then ran / imported from tackle files or directly from the [command line]().  Provider hooks additionally can be imported into tackle files and called directly.  For more information check out the [project structure](project-structure.md) docs.

## Quick Start

Since tackle box is a code generator, it makes sense for it to be able to generate the boilerplate to create providers. The quickest way to do that is with the `tackle-provider` provider which can be ran as:

```shell
tackle robcxyz/tackle-provider
```

The provider will then go through a number of configuration options such as:

- What type of license (ie Apache vs MIT vs closed source)
- Types of tests (unittest vs pytest)
- Intention of the provider (code generator vs utility)

Using this provider one can create a functional provider in minutes that when pushed to github can be called with `tackle <your org>/<your repo>`.

