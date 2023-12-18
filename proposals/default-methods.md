# Default Methods

> Status: Not implemented

This proposal is about creating a number of default methods that can be called on any hook. It is being proposed in response to a deficiency in

- flatten
- splat

Flatten

```yaml
git<-:
  commit<-:
    message:
      short: m
      type: str
      default: ""
    exec<-: command git commit {{self.flatten()}}
    exec flatten<-: command git commit {{flatten(self)}
    exec kwargs<-: command git commit {{flatten(self)}}

#
as hook with method->: command git commit "{{git.flatten()}}"
as normal hook->: command git commit "{{flatten(git)}}"
as normal hook w kwargs->: command git commit "{{flatten(git(kwargs=foo))}}"

# Does not work -> mapped as args
as declarative hook no work->: git.commit "{{git.flatten()}}"

# Does not work -> flatten a string
as declarative hook no work 2->: git.commit --kwargs "{{git.flatten()}}"

# WORKS
as declarative hook 2->: >
  git.commit --kwargs git(message="feat: foo",kwargs=defaults)
```

Declarative hook being used as args in another hook.

> Use `--kwargs` key

```yaml
foo: bar

works 1->: command {{foo}}
works 2->: command --this {{foo}}

cmd:
  message: foo
  field: bar

# Picked up by as arg
cmd no work 1->: git_commit {{cmd}}

# Picked up by as arg
kwargs work 1->: git_commit --kwargs {{cmd}}
kwargs work 2->: git_commit --kwargs cmd

# Alternatives
cmd no work 2->: git_commit {{cmd.flatten()}}
cmd work 1->: git_commit cmd...
cmd work 2->: git_commit cmd.flatten()
cmd work 3->: git_commit &&cmd
cmd work 5->: git_commit **cmd
```
