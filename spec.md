# Glint Language Specification

**Course:** CSC 404 — Survey of Programming Languages (NDU)
**Project:** Build Your Own Language (BYOL) — Week 1

## 1. Overview

Glint is a small, statically-scoped, **Turing-incomplete** scripting language.
It supports variables, arithmetic, string handling, and one level of
conditional branching (`if` / `else`). It deliberately has **no loops and
no function calls**, so no Glint program can recurse or iterate an
unbounded number of times — every program is guaranteed to halt after a
number of steps bounded by the length of its source code.

Glint uses C-style punctuation (`;` to end statements, `{ }` for blocks)
rather than newline-terminated, keyword-closed blocks — a deliberate
structural choice to keep the grammar unambiguous with a one-token
lookahead parser.

File extension: `.glint`

## 2. Data Types

| Type    | Example      |
|---------|--------------|
| Integer | `42`         |
| String  | `"hello"`    |
| Boolean | `true`, `false` |

## 3. Keywords

`var`  `if`  `else`  `say`  `true`  `false`

## 4. Operators

- Arithmetic: `+` `-` `*` `/`
- String concatenation: `..` (kept separate from `+`, so `+` always
  means numeric addition and never silently coerces a string)
- Comparison: `==` `!=` `<` `>` `<=` `>=`
- Assignment: `=`

## 5. Syntax Notes

- Every simple statement ends with `;`.
- Blocks are wrapped in `{ }` and never need a trailing `;`.
- Comments start with `//` and run to the end of the line.
- String literals support the escapes `\n`, `\t`, `\"`, `\\`.

## 6. Example Programs

**6.1 — Variables and arithmetic**
```glint
var x = 5;
var y = 10;
say x + y;
```

**6.2 — Strings and concatenation**
```glint
var name = "Ada";
say "Hello, " .. name;
```

**6.3 — Conditional branching**
```glint
var score = 75;
if (score >= 50) {
    say "Pass";
} else {
    say "Fail";
}
```

**6.4 — Operator precedence**
```glint
var result = (3 + 4) * 2 - 1;
say result;
```

**6.5 — Equality check with no else branch**
```glint
var a = 10;
var b = 20;
if (a == b) {
    say "Equal";
}
```

## 7. Formal Grammar (EBNF)

```ebnf
program         = { statement } ;

statement       = assignment
                | if_statement
                | print_statement ;

assignment      = "var" , identifier , "=" , expression , ";" ;
print_statement = "say" , expression , ";" ;
if_statement    = "if" , "(" , expression , ")" , block ,
                   [ "else" , block ] ;
block           = "{" , { statement } , "}" ;

expression      = comparison ;
comparison      = term , [ comp_op , term ] ;
comp_op         = "==" | "!=" | "<" | ">" | "<=" | ">=" ;

term            = factor , { ( "+" | "-" | ".." ) , factor } ;
factor          = unary , { ( "*" | "/" ) , unary } ;
unary           = [ "-" ] , primary ;
primary         = INTEGER
                | STRING
                | BOOLEAN
                | identifier
                | "(" , expression , ")" ;

identifier      = letter , { letter | digit | "_" } ;
INTEGER         = digit , { digit } ;
STRING          = '"' , { escape | character_no_quote } , '"' ;
escape          = "\" , ( "n" | "t" | '"' | "\" ) ;
BOOLEAN         = "true" | "false" ;

letter          = "a" .. "z" | "A" .. "Z" ;
digit           = "0" .. "9" ;
```

The `comparison → term → factor → unary → primary` chain encodes operator
precedence directly in the grammar: `*` and `/` bind tighter than `+`,
`-`, and `..`, which in turn bind tighter than the comparison operators.
This is what `parser.py` (Week 2) will walk as a recursive-descent parser.

## 8. Why Glint Is Turing-Incomplete

Turing completeness requires unbounded repetition (loops or recursion)
combined with conditional branching and unbounded memory. Glint has
conditional branching (`if`/`else`) and variables, but **no loop
construct and no function/procedure calls**, so there is no way to repeat
a block of code a variable or unbounded number of times. Every Glint
program therefore executes a number of steps proportional to its source
length and always terminates.
