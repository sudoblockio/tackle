# Memory Management

Tackle has a memory management model that defines the order of precedence when rendering variables and the ability for tackle files to pass context between one another. These areas of memory allow users to more easily access and control the context that is used to call and pass variables.  

There are four areas of memory, public, private, temporary, and existing. Public and private memory are focused on what is passed between tackle calls while temporary and existing is mainly focused on how to indent the context when building control flow in [nested blocks]().

> NOTE: Public and private memory is not to be confused with public and private hooks which relate to what hooks are externally callable.

| Type      | Mutable | Passed Between Calls | Passed Between Contexts |
|-----------|---------|----------------------|-------------------------|
| Public    | X       | X                    | X                       |
| Private   | X       |                      |                         |
| Temporary |         |                      |                         |
| Existing  |         |                      | X                       |


## Public vs Private Memory

For passing variables between files, tackle has the notion of `public` and `private` memory spaces that are differentiated based on any kind of hook call that ends in `->` or `_>` respectively.  Public contexts are exported when calling a declarative hook / tackle file / provider whereas private contexts stay local to the declarative hook / tackle file / provider. By default, non-hook calls are inserted into the public context. For instance given the following tackle file and running `tackle file.yaml -p`, with the `-p` short for `--print`, an option that prints out the output / public context:

```yaml
stuff: things
private_hook_>: input Enter value?
public_hook->: var You entered value {{private_hook}}...
```

Would result in:

```yaml
stuff: things
public_hook: You entered value <the value you entered>...
```

Public and private contexts are really only important when:

1. Operating in schema constrained environments 
- For instance you want to instantiate some schema but need to do some control flow with intermediary variables. Private memory is a good place to put those variables and not have them brought into the schema.

2. Using untrusted hooks and don't want things like passwords leaked
3. 

```yaml
goto<-:
  exec:
    type: journey
    destination_>: input Where we going? --default moon
    itinerary->: var One trip to the {{destination}}
trip->: goto
```

Which when run with `tackle file.yaml -p` would prompt the user and return:

```yaml
trip:
  type: journey
  itinerary: One trip to the moon
```

Where we can see that `destination` was not included in the output because it is a private hook. This shows how if you need to control the schema, private hooks are an good way manage what is return it while still having the ability to use internal variables and call internal actions.


### Existing Context

The existing context is the public context that is passed when calling another tackle file or providers from within a tackle file. It is helpful if you want to build context in one file and then use it in another. For instance a common pattern is to have a data file that holds variables that are then used to render / resolve underlying logic. In the following example we can see the initial file call another file and then use that context to perform an action.

#### **`calling-tackle.yaml`**
```yaml
globals->: tackle globals.yaml --find_in_parent --merge
#...
do->: print {{stuff}}
```

Which could then call a file which asks for things like environment and then indexes some data (many ways to do this) allowing the previous file to access variables specific to the environment.

#### **`globals.yaml`**
```yaml
environment->: select --choices ['dev','prod']
dev_>:
  stuff: things
prod_>:
  stuff: more things
merge->: get {{environment}} --merge
```

### Temporary Context

When parsing [blocks]() and other hooks that parse their own individual context such as the [match]() hook, an additional context is built so that users don't need to provide the full path to variables that are on the same level. For instance given this block hook, the following would run:

```yaml
trips->:
  for:
    - space
    - the moon
    - mars
  destination->: "{{item}}"
  info_>: print Let's go to {{destination}}!
```

Notice how within the `trip` block, the field `destination` can be referenced directly without its full path which would be `trips[index].destination`, something that would be a serious pain in complicated nested logic.  

## Render Context Precedence

When variables are rendered, they can use any number of different contexts based on an order of precedence described below.

1. Temporary
2. Public
3. Private
4. Existing
