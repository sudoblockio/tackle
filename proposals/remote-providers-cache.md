---
id:
title: Remote Provider Cache
status: wip
description:
issue_num: 255
blockers: []
---
[//]: # (--start-header--DO NOT MODIFY)

[//]: # (--end-header--start-body--MODIFY)


# Remote Provider Cache

### Cache Path

- org
- repo
- version
  - base
- file / path?  
  - checksum: str
  - hooks: list


### Imports + Change Detection

#### Local

- import (current)
- checksums
- pyc
  - would need to compile

- using cache
  - release cache
    - located in providers dir
      - irrespective of native vs remote
    - based on version of tackle
    - this would allow version controlling native providers

  - provider locals
    - file in each provider that can freeze versions
    - to create
      - run command
        - `tackle <target> --freeze` -> looks up version from remote and pins to that
      - runs a special parser that does not run any hook except tackle / import hooks and catalogues each provider
        - can be run with additional options to pin back to the previous release
    - if file exists
      - assert that all the providers exist in path
      - store object in providers either as lazy


#### Remote

- latest
  - pulls
- version
  - pinned

##### Current

- latest defaults to true
- If version is not given then need to
  - Check if there are any versioned releases on each get
  - If there are, then use that one
  - If not get the default branch and use that


### Sequence

- read cache
  - if it doesn't exist
    - build it (easy+long) / copy it (hard+fast+needs build step)
- read checksum of providers from cache
  - checksums take almost as long as
- compare with native checksum

### Cache Schema

For providers:

**.tackle.lock.yaml**
```yaml
tackle_version: v0.6.0  # From tackle
providers:
  - type: native
    version: v0.6.0  # When different from above, not changed
  - name: a-remote-provider
    path: org/repo
    version: v1.0
    hooks:

  - name: a-local-provider
    type: local
    path: /home/path/...
```

Logic:
- If type and type == 'native'
  - path = providers_dir / tackle-{{version}}
  - for i in path (iter over providers)

**.tackle.lock.yaml**
```yaml
tackle_version: v0.6.0  # From tackle
provider_dir:
providers:
  - name: collections
    path: tackle/v0.6.0/collections
  - name: console
    path: tackle/v0.6.0/console
```

