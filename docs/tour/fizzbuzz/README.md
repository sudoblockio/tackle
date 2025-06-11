# tackle fizzbuzz

If you are not familiar with [fizzbuzz](https://wiki.c2.com/?FizzBuzzTest), it is one of the most basic / prolific programming interview questions with the following requirements:

- Write a function that takes an integer input
- Print `fizz` if divisible by 3
- Print `buzz` if divisible by 5
- Print the number if it is not divisible by either 3 or 5
- Thus for numbers like 15, we would print out `fizzbuzz`

Solving this problem many ways in tackle demonstrates some of tackle's flow control mechanisms.

### Solutions

[//]: # (--start-table--)

- [Simple conditionals](conditionals.yaml)
- [List of conditionals](list-conditionals.yaml)
- [Loop of conditionals](loop-conditional.yaml)
- [Match case](match-case.yaml)
- [Appending to a list](list-append.yaml)
- [Validator](validator.yaml)

[//]: # (--end-table--)

## Examples

[//]: # (--start-sections--)


### Simple conditionals

Here we can see simple conditional statements being run both as a single line and expanded over multiple lines.

```yaml
i->: "{{int(input('Enter a number...'))}}"
fizz->: print fizz --if "i %3 == 0"
buzz->: print buzz --if "i % 5 == 0"
non-fizz:
  ->: print {{i}}
  if: "'fizz' not in this and 'buzz' not in this"

```

### List of conditionals

When tackle parses a list it can do a conditional on each item and then reference itself

```yaml
(input int)<-:
  output:
    - ->: print fizz --if "input % 3 == 0"
    - ->: print buzz --if "input % 5 == 0"
    - ->: print {{input}} --if output|length==0
```

### Loop of conditionals

Here we have a list of objects which we can loop over and then use within a

```yaml
(input int)<-:
  values:
    - modulo: 3
      output: fizz
    - modulo: 5
      output: buzz
  fizzbuzz->: print {{i.output}} --for i in values --if input%i.modulo==0
  input_print->: print {{input}} --if not fizzbuzz

```

### Match case

Tackle has a match hook which can have keys rendered in order to support cascading conditionals

```yaml
<-:
  input: int
  args: ['input']
  exec:
    ->: match
    case:
      "{{input % 15 == 0}}->": print fizzbuzz
      "{{input % 3 == 0}}->": print fizz
      "{{input % 5 == 0}}->": print buzz
      _->: print {{input}}

```

### Appending to a list

Here we can see a list `output` being declared which can then be appended to before printing the output with a conditional

```yaml
(input int)<-:
  output: [ ]
  fizz->: append output fizz --if "input % 3 == 0"
  buzz->: append output buzz --if "input % 5 == 0"
  out->: print "{{join(output)}}" --if output|length!=0 --else {{print(input)}}
```

### Validator

Logic can be embedded on creation of a field in a hook through a validator which can also check against other fields

```yaml
<-:
  input:
    type: Union[int, str]
    validator:
      fizzbuzz->: returns fizzbuzz --if "v % 15 == 0"
      fizz->: returns fizz --if "v % 3 == 0"
      buzz->: returns buzz --if v%5==0
      non-fizz->: return {{v}}
  args: ['input']
  exec:
    ->: print {{input}}

```

[//]: # (--end-sections--)
