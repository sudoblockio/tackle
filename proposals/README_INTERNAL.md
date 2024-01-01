# Tackle Proposal System

This directory is laid out in a way to achieve the following:

1. Single place where new ideas / syntaxs can be tracked and worked on over time
2. Provide a single document to overview all the proposals aligning blockers and priorities
2. Create GH issues with the proposal documents which can be kept in sync from the repo to the issue

To do this we rely on the following pattern:

- Documents have a "frontmatter" section with metadata that is the source of truth of the proposal tracking things like title, description, and issue number
- Each time a document changes in this directory, the tackle script is run which
  - Pushes changes to the issue
  - Updates the README in this directory and creates a PR with those changes

In order to run these scripts locally you will need an environment variable GITHUB_TOKEN with a PAT with `repo.public` permissions.