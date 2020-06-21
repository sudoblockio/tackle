
# TTD
---

### Operators
- inquirer
  - [ ] Get pty process running to launch pseudo shell
  - [ ] Allow for returning pipe output from popen
  - [ ] Mock pseudo shell process to be rolled out across testing
- [ ] Jinja templates folder fallback
- [ ] Requests...
- [ ] git
- [ ] ssh
- [ ] Templating operators
  - [ ] tfvars
  - [ ] terragrunt?
- [ ]

### Operator Parsing
- [x] Move no_input to run operator section
- [x] Include new parameter for default fallback
- [ ] Handler attribute
- [ ] Validation attribute
- [ ] Filter attribute
- [ ] Before / After operator hook
- [ ] Fallback override

### Main
- [x] nuki....
- [ ] Choose option Accept input for template name
- [ ] Accept yaml file inputs
- [ ] Catch `nuki.*` files when walking directory and parse
    - Partially implemented
    - Need to add valid_context_files from `repository.py` in `generate.py`
- [ ]

### Features
- [ ] Modules for complex operations
- [ ] Consider RPC interface for executing operators
    - [ ] Instead of calling `execute`, call a method from base that has logic to inform target
- [ ]

### Docs
- [ ] Add sphinx `autodoc` for API reference
- [ ]
