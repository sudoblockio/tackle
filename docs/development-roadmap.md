# Development Roadmap

Tackle is still a work in progress with the following new features planned.

- [IDE Autocomplete](#ide-autocomplete)
- [Providers allowing import of jinja extensions](#providers-allowing-import-of-jinja-extensions)
- [Provider registry](#provider-registry)
- [Rewrite in compiled language](#rewrite-in-compiled-language)

## IDE Autocomplete

Need to extract the json schema from each hook and upload that to [schemastore.org/json/](https://www.schemastore.org/json/) with appropriate [catalog.json](https://www.schemastore.org/api/json/catalog.json) file.

## Providers allowing import of jinja extensions

Providers give a good import abstraction so it would be cool to be able to allow dynamically importing of various jinja extensions as well.

## Provider registry

If this tool gets enough traction, a provider registry will be made to allow users to find new hooks and providers similar to the [Terraform Registry](https://registry.terraform.io/) and [Ansible Galaxy](https://galaxy.ansible.com/. Users should be able to link a GitHub repo to the registry and provide metadata that will allow users to easily be able to search for the hook / provider that they need with auto-generated documentation similar to how the docs show [hook docs](providers/Prompts/index.md).

## Rewrite in compiled language

If this tool gets enough traction, it will be rewritten in a compiled language, most likely Rust. The current version is considered experimental with different patterns for expressing logic being formed. Future versions will maintain compatibility with python hooks and also support hooks being written in other languages.
