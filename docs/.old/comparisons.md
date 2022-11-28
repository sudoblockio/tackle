# Comparisons to Other Tools

For the purpose of better understanding the applicability of tackle, this document tries to make some comparisons

[//]: # (TODO: )

## Code Generation

Most code generators out there have only one way of building a render context.  For instance:

- [create-react-app](https://github.com/facebook/create-react-app)
  - No prompting
  - All configuration options baked in
- [cookiecutter](https://github.com/cookiecutter/cookiecutter)
  - Input prompts
  - User inputs based on a json config file
- [openapi-generator](https://github.com/OpenAPITools/openapi-generator)
  - Input spec
  - User points to an OpenAPI spec

Tackle being more of a DSL allows all these configuration options in a completely modular way with the only catch, that you need to explicitly declare all the functionality in a tackle file.  This tutorial walks through how to setup code generators based on each of the above patterns.