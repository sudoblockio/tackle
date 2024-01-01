---
id:
title: Native Providers in Individual Repos
status: wip
description: Move the majority of the providers to remote locations
issue_num: 254
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

[//]: # (--end-header--start-body--MODIFY)

Over time the intention will likely be to move most of the native providers to a version controlled repo that is imported. Before doing this, we need to implement a better caching strategy for how providers are pulled in at startup.

**Advantages**

- Improve start up times
  - Hooks with dependencies which will be removed take the longest to import, thus native hooks will be faster
  > Startup times are reasonable now that pydantic is no longer in context
  > Main issue now is times for loading providers
- Users can more consistently use an API if they choose,  

**Issues**

- Current way of calling remote hooks is through an import
  - `v->: import sudoblockio/tackle-...`
    - This is a lot
  - If this is to be done properly, we should have another way through a version file which is by default used to match a hook to
- Will need to improve speed hooks can be used.
- Will have to build registry of hooks
- Rebuild docs and how that is maintained

#### Hooks to be moved

Mainly it is hooks with dependencies. Thus native tackle should be able to ship without any hooks that need to have requirements.

- console? - rich
- git
- k8s
- ssh
- postgres
- web? - Only requests

## TTD

#### Cache

- Build cache for remote providers
  - Should have some kind of update command and some startup / background process
  - Background process will be weird as user would not necessarily know what is making all kinds of calls.
  - Command is easy and should be done
  - Logic should be that tackle first looks in the provider dir for some kind of freeze versions file, terraform has it, similar to pip, and use that as the versions of the dependencies that need to be checked out.
  - Once hook is used, those references are whats used to checkout / clone the hook

#### Version File

- Track which version of a hook is being used in a tackle file.
  - Have ability to freeze dependencies
  - If you use a remote more than once it should not have to re-init

#### Registry

- Will need a process to discover new hooks.
- Initially this can be a static file
- Over time this should be a GH action that queries GH for repos that satisfy condition
- UI would be cool

#### Docs

- Registry will feed service discovery for docs
- If UI is together, then it should integrate with that

