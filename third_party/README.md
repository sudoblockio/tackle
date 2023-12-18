# Third Party Providers

This is a directory of providers that don't ship natively with tackle. They generally:

- Integrate with external tools like kubernetes or terraform
- Have additional requirements that need to be installed
- Have their versioning managed outside of the main tackle distribution
- Can include declarative hooks and templates (native hooks do not have either)
- Are more opinionated

These are WIP as a packaging method needs to be implemented. For now they can be used via an import hook specifying the


TODO:

- Table with linked third party providers in this document
  - Code gen it similarly as docs
  - Loop though providers building metadata
  - Generate table here and in docs
- Make decision on how these are packaged
  - Bazel - Somewhat complicated as copybara would need to be used since the import / release mechanism should go through version control
  - Metarepo - Need to create new repos for each and probably improve metarepo hook to support committing across many repos
