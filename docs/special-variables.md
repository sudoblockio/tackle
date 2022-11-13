# Special Variables

A number of special variables exist for using within tackle files to gain access to common things.

### Directories and Files

- `cwd` - Current working directory  
- `home_dir` - Home directory
- `calling_directory` - The directory tackle was called from
- `calling_file` - The path to the tackle file that was first called
- `current_file` - The current tackle file's name
- `current_directory` - The directory of the input tackle file.
- `tackle_dir` - Directory where tackle config is, ie `~/.config/tackle`
- `provider_dir` - Directory where tackle config is, ie `~/.config/tackle/providers`
- `xdg_cache_home` - XDG [cache dir](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- `xdg_config_dirs` - XDG [config dirs](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- `xdg_config_home` - XDG [config home](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- `xdg_data_dirs` - XDG [data dirs](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- `xdg_data_home` - XDG [data dir](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- `xdg_runtime_dir` - XDG [runtime dir](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- `xdg_state_home` - XDG [state home](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)


### System Properties

- `system` - OS (ie `Darwin`, `Linux`, `Windows`). Same as python's `platform.system()`
- `platform` - OS with kernel, ie `Linux-5.8.0-45-generic-x86_64-with-glibc2.29`
- `version` - Kernel's release, ie `#51~20.04.1-Ubuntu SMP Tue Feb 23 13:46:31 UTC 2021`
- `processor` - Processor architecture, ie `x86_64`. Same as `platform.processor()`
- `architecture` - Further architecture info, ie `('64bit', 'ELF')`
- `lsb_release` - Same as linux's lsb_release, ie `Ubuntu 20.04.4 LTS (Focal Fossa)`

### Tackle Internals

See [memory management](memory-management.md) docs for more details on the differences between contexts.

- `this` - The public context from normal keys and hooks called with `->`
- `public_context` - The public context from normal keys and hooks called with `->`
- `private_context` - The private context from hooks called with `_>`
- `existing_context` - The existing context passed into blocks
- `temporary_context` - The temporary context when parsing blocks
- `key_path` - A list of keys to identify position in document
- `key_path_block` - Same as key path but normalized for being within a block
