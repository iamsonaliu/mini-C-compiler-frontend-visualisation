# Mini-C Compiler Front-End Visualizer

An interactive compiler front-end visualization tool for a simplified subset of C (Mini-C).  
It performs **lexical analysis**, **syntax parsing**, and **basic semantic checks** — with  
a live parse tree rendered in your browser. No code is executed.

---

## Project Structure

```
mini-c-compiler/
├── backend/
│   ├── app.py           # Flask API server
│   ├── lexer.py         # PLY lexer (tokenizer)
│   ├── parser.py        # PLY parser (grammar + parse tree)
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

1. Type Mini-C code into the editor (or load an example from the dropdown).
2. Click **Validate** (or press `Ctrl+Enter`).
3. Inspect results across four tabs:
   - **Tokens** — full token stream with types and line numbers
   - **Errors** — lexical, syntax, and semantic errors with explanations
   - **Parse Tree** — interactive D3 tree (zoom/pan with mouse or buttons)
   - **Symbols** — all declared variables with type and scope

---

## Mini-C Language Reference

### Supported Features

| Feature              | Example                        |
|----------------------|--------------------------------|
| Integer variables    | `int x = 10;`                  |
| Float variables      | `float pi = 3.14;`             |
| Char variables       | `char c = 'A';`                |
| Arithmetic           | `int r = a + b * 2;`           |
| Comparison operators | `a >= b`, `x == 0`, `a != b`  |
| Logical operators    | `a && b`, `x \|\| y`, `!flag` |
| If / else            | `if (x > 0) { ... } else { }` |
| While loop           | `while (i < 10) { ... }`       |
| Return statement     | `return x + y;`                |
| Printf               | `printf("value: %d", x);`      |
| Block scoping        | `{ int inner = 5; }`           |
| Line comments        | `// this is a comment`         |
| Block comments       | `/* multi-line */`             |

### Not Supported

- Pointers, arrays, structs
- Function definitions (only `main`-style blocks)
- `scanf`, `for` loop
- Type casting
- `#include`, preprocessor directives

---

## Mini-C Grammar (BNF)

```
program         → statement_list

statement_list  → statement_list statement
                | statement

statement       → declaration_stmt
                | assignment_stmt
                | if_stmt
                | while_stmt
                | return_stmt
                | printf_stmt
                | block
                | expr_stmt

declaration_stmt → type_spec ID ;
                 | type_spec ID = expression ;

type_spec       → int | float | char | void

assignment_stmt → ID = expression ;

if_stmt         → if ( expression ) block
                | if ( expression ) block else block

while_stmt      → while ( expression ) block

return_stmt     → return expression ;
                | return ;

printf_stmt     → printf ( arg_list ) ;

arg_list        → arg_list , expression
                | expression

block           → { statement_list }
                | { }

expr_stmt       → expression ;

expression      → expression + expression
                | expression - expression
                | expression * expression
                | expression / expression
                | expression % expression
                | expression == expression
                | expression != expression
                | expression < expression
                | expression > expression
                | expression <= expression
                | expression >= expression
                | expression && expression
                | expression || expression
                | ! expression
                | - expression
                | ( expression )
                | ID
                | NUMBER_INT
                | NUMBER_FLOAT
                | CHAR_LITERAL
                | STRING_LITERAL
```

---

## Semantic Checks

| Check                       | Example Error                                     |
|-----------------------------|---------------------------------------------------|
| Variable used before declared | `y = 5;` (no prior `int y;`)                   |
| Undefined variable in expression | `return x + z;` (z not declared)            |
| Duplicate declaration       | `int x = 1; int x = 2;` in same scope            |
| Division by literal zero    | `int r = a / 0;` (warning)                        |

---

## Test Cases

### ✓ Valid Code
```c
int main() {
    int a = 10;
    int b = 3;
    int c = a + b * 2;
    if (c > 15) {
        return 1;
    } else {
        return 0;
    }
}
```

### ✗ Undeclared Variable
```c
int main() {
    x = 10;          // ERROR: x not declared
    return x;
}
```

### ✗ Duplicate Declaration
```c
int main() {
    int count = 0;
    int count = 5;   // ERROR: count already declared
}
```

### ✗ Syntax Error
```c
int main() {
    int x = 10      // ERROR: missing semicolon
    return x;
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
  "symbol_table": [ { "name": "x", "type": "int", "scope": "global", "line": 1 } ],
  "status": "success",
  "total_errors": 0,
  "total_warnings": 0,
  "final_message": "✓ Code is syntactically and semantically correct!"
}
```