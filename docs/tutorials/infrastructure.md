# Infrastructure Management Tutorials

TODO

- [ ] Combining contexts
- [ ] Parent child pattern
- [ ] Calling tools (ansible / tf / k8s)
- [ ] Helpful patterns


## Design

- Parent/child design pattern
  - Parent tackle file
    - Stores global variables that are shared between all the modules
    - Can contain selectors for environment / region / kube context
    - Contains a `./hooks` directory that imports the appropriate hooks for running tools
  - Child tackle file
    - Stores deployment specific variables
    - Calls the appropriate tool (ie ansible, terraform, helm, kubectl)

### Parent Design Patterns

##### Storing global variables

- Convention is to store global variables in a `globals.yaml` file which

### Child Design Patterns

```yaml
global->: tackle globals.yaml --find_in_parent --merge

```



