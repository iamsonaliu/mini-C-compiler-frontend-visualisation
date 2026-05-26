# Mini-C Compiler Front-End Visualizer

An interactive compiler front-end visualization tool for a simplified subset of C (Mini-C).  
It performs **lexical analysis**, **syntax parsing**, and **enhanced semantic checks** — with  
a live parse tree rendered in your browser. No code is executed.

---

## Project Structure

```
mini-c-compiler/
├── backend/
│   ├── app.py           # Flask API server
│   ├── lexer.py         # Regex-based lexer (tokenizer)
│   ├── parser.py        # Recursive-descent parser (grammar + parse tree)
│   ├── parse_tree.py    # ParseTreeNode class
│   └── semantic.py      # Semantic analyzer + symbol table
├── frontend/
│   └── templates/
│       └── index.html   # Single-file frontend (D3.js tree)
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Install Python Dependencies

```bash
cd mini-c-compiler
pip install -r requirements.txt
```

### 2. Run the Server

```bash
cd backend
python app.py
```

### 3. Open in Browser

Visit: [http://localhost:5000](http://localhost:5000)

---

## How to Use

1. Type Mini-C code into the editor (or load an example from the grouped dropdown).
2. Click **Compile** (or press `Ctrl+Enter`).
3. Inspect results across four tabs:
   - **Tokens** — full token stream with types and line numbers
   - **Errors** — lexical, syntax, semantic errors and warnings with explanations
   - **Parse Tree** — interactive D3 tree (zoom/pan with mouse or buttons)
   - **Symbols** — all declared variables and functions with type, scope, and usage status

---

## Mini-C Language Reference

### Supported Features

| Feature                  | Example                              |
|--------------------------|--------------------------------------|
| Integer variables        | `int x = 10;`                        |
| Float variables          | `float pi = 3.14;`                   |
| Char variables           | `char c = 'A';`                      |
| Arithmetic               | `int r = a + b * 2;`                 |
| Comparison operators     | `a >= b`, `x == 0`, `a != b`         |
| Logical operators        | `a && b`, `x \|\| y`, `!flag`        |
| If / else / else-if      | `if (x > 0) { } else if { } else { }` |
| While loop               | `while (i < 10) { ... }`             |
| **For loop**             | `for (int i = 0; i < 10; i++) { }`   |
| **Do-while loop**        | `do { ... } while (x > 0);`          |
| **Break / Continue**     | `break;` / `continue;`               |
| **Increment / Decrement**| `i++`, `++i`, `i--`, `--i`            |
| **Compound assignment**  | `x += 5`, `x -= 3`, `x *= 2`, `x /= 4` |
| **Switch / Case / Default** | `switch (x) { case 1: ... break; default: ... }` |
| **Function definitions** | `int add(int a, int b) { return a+b; }` |
| **Function calls**       | `int r = add(3, 5);`                 |
| Return statement         | `return x + y;`                      |
| Printf                   | `printf("value: %d", x);`            |
| Scanf                    | `scanf("%d", x);`                    |
| Block scoping            | `{ int inner = 5; }`                 |
| Line comments            | `// this is a comment`               |
| Block comments           | `/* multi-line */`                    |

### Not Supported

- Pointers, arrays, structs, unions
- Type casting
- `#include`, preprocessor directives
- String operations
- Dynamic memory (`malloc`, `free`)

---

## Mini-C Grammar (BNF)

```
program         → statement_list

statement_list  → statement_list statement
                | statement

statement       → declaration_stmt
                | assignment_stmt
                | compound_assign_stmt
                | if_stmt
                | while_stmt
                | for_stmt
                | do_while_stmt
                | switch_stmt
                | break_stmt
                | continue_stmt
                | return_stmt
                | printf_stmt
                | scanf_stmt
                | function_decl
                | block
                | expr_stmt

declaration_stmt → type_spec ID ;
                 | type_spec ID = expression ;

type_spec       → int | float | char | void

assignment_stmt → ID = expression ;

compound_assign_stmt → ID += expression ;
                     | ID -= expression ;
                     | ID *= expression ;
                     | ID /= expression ;

if_stmt         → if ( expression ) block
                | if ( expression ) block else block
                | if ( expression ) block else if_stmt

while_stmt      → while ( expression ) block

for_stmt        → for ( for_init ; expression ; for_update ) block

for_init        → declaration_stmt_no_semi
                | assignment_expr
                | ε

for_update      → assignment_expr
                | ID ++
                | ID --
                | ++ ID
                | -- ID
                | compound_assign_expr
                | ε

do_while_stmt   → do block while ( expression ) ;

switch_stmt     → switch ( expression ) { case_list }

case_list       → case_clause case_list
                | default_clause
                | ε

case_clause     → case expression : statement_list

default_clause  → default : statement_list

break_stmt      → break ;

continue_stmt   → continue ;

return_stmt     → return expression ;
                | return ;

printf_stmt     → printf ( arg_list ) ;

scanf_stmt      → scanf ( arg_list ) ;

function_decl   → type_spec ID ( param_list ) block

param_list      → param_list , param
                | param
                | ε

param           → type_spec ID

arg_list        → arg_list , expression
                | expression

block           → { statement_list }
                | { }

expr_stmt       → expression ;

expression      → expression binop expression
                | ! expression
                | - expression
                | ++ expression
                | -- expression
                | expression ++
                | expression --
                | ( expression )
                | ID ( arg_list )        // function call
                | ID
                | NUMBER_INT
                | NUMBER_FLOAT
                | CHAR_LITERAL
                | STRING_LITERAL

binop           → + | - | * | / | %
                | == | != | < | > | <= | >=
                | && | ||
```

---

## Semantic Checks

| Check                            | Example Error                                              |
|----------------------------------|------------------------------------------------------------|
| Variable used before declared    | `y = 5;` (no prior `int y;`)                               |
| Undefined variable in expression | `return x + z;` (z not declared)                            |
| Duplicate declaration            | `int x = 1; int x = 2;` in same scope                      |
| Division by literal zero         | `int r = a / 0;` (warning)                                  |
| Unused variable                  | `int x = 5;` (x never referenced) — warning                 |
| Type mismatch on assignment      | `int x = 3.14;` — warning                                   |
| **`break` outside loop/switch**  | `break;` at top level → error                               |
| **`continue` outside loop**      | `continue;` at top level → error                             |
| **Duplicate function definition**| `int f() {} int f() {}` → error                             |
| **Wrong argument count**         | `add(1,2,3)` when `add` takes 2 → error                     |
| **Call to undefined function**   | `foo(5);` when `foo` not defined → warning                   |

---

## Test Cases

### ✓ For Loop
```c
int sum = 0;
for (int i = 0; i < 10; i++) {
    sum += i;
}
return sum;
```

### ✓ Do-While Loop
```c
int count = 0;
int x = 100;
do {
    x = x / 2;
    count++;
} while (x > 1);
return count;
```

### ✓ Nested Loops with Break/Continue
```c
int sum = 0;
for (int i = 0; i < 20; i++) {
    if (i % 2 == 0) {
        continue;
    }
    if (i > 15) {
        break;
    }
    sum += i;
}
return sum;
```

### ✓ Switch-Case
```c
int day = 3;
int type = 0;
switch (day) {
    case 1:
        type = 1;
        break;
    case 2:
        type = 1;
        break;
    case 3:
        type = 2;
        break;
    default:
        type = 0;
        break;
}
return type;
```

### ✓ Functions
```c
int add(int a, int b) {
    return a + b;
}

int main() {
    int sum = add(3, 5);
    printf("Sum: %d", sum);
    return 0;
}
```

### ✓ Compound Assignment & Increment
```c
int x = 10;
x += 5;
x -= 3;
x *= 2;
x /= 4;
x++;
return x;
```

### ✗ Break Outside Loop
```c
int x = 5;
break;        // ERROR: break not in loop or switch
return x;
```

### ✗ Wrong Argument Count
```c
int add(int a, int b) {
    return a + b;
}
int main() {
    int r = add(1, 2, 3);   // ERROR: expects 2 args, got 3
    return r;
}
```

---

## API Reference

**POST** `/api/compile`

**Request body:**
```json
{ "code": "int x = 5;" }
```

**Response:**
```json
{
  "tokens": [ { "type": "INT", "value": "int", "line": 1 }, ... ],
  "lexical_errors": [],
  "syntax_errors": [],
  "parse_tree": { "name": "Program", "children": [...] },
  "semantic_errors": [],
  "semantic_warnings": [],
  "symbol_table": [ { "name": "x", "type": "int", "scope": "global", "line": 1, "used": false } ],
  "status": "success",
  "total_errors": 0,
  "total_warnings": 1,
  "final_message": "✓ Code is syntactically and semantically correct! (1 warning(s))"
}
```