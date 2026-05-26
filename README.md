# 🚀 Mini-C Compiler Front-End Visualizer v2.0

An elegant, premium, interactive web-based compiler front-end visualization tool designed for a comprehensive subset of C (known as **Mini-C**). 

This project decomposes compiler frontend operations into visually inspectable, step-by-step interactive stages: **Lexical Analysis (Tokenization)**, **Pure Recursive-Descent Parsing (AST Generation)**, and **Advanced Semantic Analysis (Scope, Type, and Context Validation)**.

Featuring a futuristic dark-theme interface with an adjustable/resizable split-pane workspace, an interactive zoomable/pannable D3.js parse tree, and robust error/warning logging.

---

## ✨ Features & Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                              USER CODE                                 │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ (HTTP POST)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                               BACKEND                                  │
│                                                                        │
│  ┌───────────────────────┐    ┌───────────────────────┐                │
│  │   lexer.py            │───>│   parser.py           │                │
│  │   • Token stream      │    │   • Recursive Descent │                │
│  │   • Regex matching    │    │   • AST Generation    │                │
│  └───────────────────────┘    └───────────┬───────────┘                │
│                                           │ (ParseTreeNode)            │
│                                           ▼                            │
│                               ┌───────────────────────┐                │
│                               │   semantic.py         │                │
│                               │   • Scope / Type check│                │
│                               │   • Warnings / Errors │                │
│                               └───────────┬───────────┘                │
└───────────────────────────────────────────┼────────────────────────────┘
                                            │ (JSON Response)
                                            ▼
┌────────────────────────────────────────────────────────────────────────┐
│                               FRONTEND                                 │
│                                                                        │
│  ┌───────────────────────┐    ┌───────────────────────┐                │
│  │   Adjustable Editor   │    │   Results Console     │                │
│  │   • Split resizing    │    │   • Zoomable Parse Tree│                │
│  │   • Real-time compile │    │   • Interactive Tabs  │                │
│  └───────────────────────┘    └───────────────────────┘                │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. 🎨 The Frontend (React + Vite)
- **Adjustable Split Workspace**: A custom-engineered slider separator allows you to dynamically expand or contract the code editor and results panel to match your screen layout preferences.
- **D3.js Collapsible Parse Tree**: High-fidelity visual tree visualization with support for interactive node collapsing, panning, and mouse-wheel zooming.
- **Tabbed Results Interface**:
  - **Tokens**: Clear list representing the scanned token stream, categorized by token types and annotated with their corresponding source lines.
  - **Errors & Warnings**: Highlights lexical, syntax, and semantic errors with distinct UI indicator badges and warning flags (e.g., unused variables or unsafe division by zero).
  - **Parse Tree**: The visual representation of the abstract grammar node structure.
  - **Symbol Table**: Displays active symbols, their types, declared lines, pointer depth, array dimensions, parameter specifications, and current scope levels.

### 2. ⚡ The Hand-Written Parser & Lexer
- **Custom Lexer (`lexer.py`)**: Built from scratch using Python's regular expression framework. Scans keywords, numeric constants (integers and floats), character/string literals, complex operators, pointer references, and block/inline comments.
- **Recursive-Descent Parser (`parser.py`)**: A pure-Python hand-written predictive parser implementing recursive-descent logic with operator precedence climbing.
  - **Error Recovery**: Equipped with synchronization points (`sync()`) that discard erroneous tokens up to the nearest statement delimiter (`;`, `}`, `case`, `default`) to continue parsing and capture multiple syntax issues in a single pass.

### 3. 🛡️ Advanced Semantic Analyzer (`semantic.py`)
Provides production-like safety checks on the parsed AST:
- **Layered Scope Resolution**: Implements block scoping and global namespaces, matching identical variable declarations inside nesting blocks.
- **Duplicate Declaration Detection**: Flags compiler errors when the same identifier is declared twice in a single scope.
- **Undefined Reference Check**: Ensures variables and functions are declared before they are referenced.
- **Loop-Context Tracking**: Validates that `break` and `continue` keywords are exclusively placed inside looping constructs (`while`, `for`, `do-while`).
- **Function Signature Validation**: Maps parameters, parameter types, and validates invocation argument counts.
- **Array & Pointer Syntheses**: Performs type checks on array subscripts (must be integer index expressions), tracks pointer depth, address-of (`&`), and dereferencing (`*`) operations.
- **Unused Variable Diagnostics**: Triggers compiler warnings for declared variables that are never referenced.
- **Division by Zero Warnings**: Analyzes division denominators to report warnings for divisions by literal zeros.

---

## 🛠️ Tech Stack

* **Frontend**: React (v19), Vite (v8), D3.js (v7), and Vanilla CSS (featuring custom glassmorphism components, CSS grids, flexbox, and smooth micro-animations).
* **Backend**: Python 3, Flask (v2.x) with custom tokenizer and compiler validation engines.

---

## 🚀 Quick Start & Installation

Ensure you have [Python 3.x](https://www.python.org/downloads/) and [Node.js](https://nodejs.org/) installed.

### 1. Set Up the Backend
Navigate to the `backend/` folder, activate a virtual environment, and start the Flask server:

```bash
# Navigate to backend
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/macOS:
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt

# Run the Flask app (runs on port 5000)
python app.py
```

### 2. Set Up the Frontend
In a new terminal window, navigate to the `react-frontend/` directory, install the Node modules, and launch the Vite dev server:

```bash
# Navigate to frontend
cd react-frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

Open your browser and navigate to the local address displayed by Vite (typically **`http://localhost:5173`**).

---

## 📘 Mini-C Language Grammar (BNF)

The compiler frontend parses the following language specification:

```bnf
program              → statement_list

statement_list       → statement_list statement
                     | statement

statement            → declaration_stmt
                     | assignment_stmt
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
                     | function_def
                     | block
                     | expr_stmt

declaration_stmt     → type_spec declarator ( = expression )? ;

type_spec            → int | float | char | void

declarator           → * declarator            /* Pointers */
                     | direct_declarator

direct_declarator    → ID
                     | direct_declarator [ NUMBER_INT ]  /* Arrays */

assignment_stmt      → expression assign_op expression ;

assign_op            → = | += | -= | *= | /= | %=

if_stmt              → if ( expression ) statement ( else statement )?

while_stmt           → while ( expression ) statement

for_stmt             → for ( declaration_stmt | expr_stmt | ; ) ( expression )? ; ( expression )? ) statement

do_while_stmt        → do statement while ( expression ) ;

switch_stmt          → switch ( expression ) { case_list default_clause? }

case_list            → case_list case_clause
                     | case_clause

case_clause          → case expression : statement_list

default_clause       → default : statement_list

break_stmt           → break ;

continue_stmt        → continue ;

return_stmt          → return ( expression )? ;

printf_stmt          → printf ( STRING_LITERAL ( , expression )* ) ;

scanf_stmt           → scanf ( STRING_LITERAL ( , & ID )* ) ;

function_def         → type_spec declarator ( parameter_list ) block

block                → { statement_list? }

expression           → logical_or_expr

logical_or_expr      → logical_and_expr ( || logical_and_expr )*

logical_and_expr     → equality_expr ( && equality_expr )*

equality_expr        → relational_expr ( ( == | != ) relational_expr )*

relational_expr      → additive_expr ( ( < | > | <= | >= ) additive_expr )*

additive_expr        → multiplicative_expr ( ( + | - ) multiplicative_expr )*

multiplicative_expr  → unary_expr ( ( * | / | % ) unary_expr )*

unary_expr           → ( ++ | -- | & | * | + | - | ! ) unary_expr
                     | postfix_expr

postfix_expr         → primary_expr ( ++ | -- )
                     | ID ( argument_list? )   /* Function Call */
                     | ID [ expression ]       /* Array Subscription */

primary_expr         → ID
                     | NUMBER_INT
                     | NUMBER_FLOAT
                     | CHAR_LITERAL
                     | STRING_LITERAL
                     | ( expression )
```

---

## 🧪 Try It Out! (Sample Program)

Test the robustness of the front-end parser and scope analysis by loading this comprehensive Mini-C snippet:

```c
// Rich Mini-C Demo (Functions, Loops, Pointers, Arrays)
int add(int a, int b) {
    return a + b;
}

int main() {
    int arr[3];
    arr[0] = 10;
    arr[1] = 20;

    int sum = 0;
    for (int i = 0; i < 2; i++) {
        sum = add(sum, arr[i]);
    }

    int *p = &sum;
    *p += 5;

    printf("Total sum: %d", sum);
    return sum;
}
```

This snippet showcases:
1. **Functions**: Declarations, definitions, returning expressions, parameter lists, and nested validation.
2. **Arrays**: Declaration `arr[3]` and indexed assignments `arr[0] = 10`.
3. **Control Flow**: A standard block-scoped `for` loop with initializer declaration.
4. **Pointers**: Address-of assignments `&sum`, pointer declarations `int *p`, and pointer dereferencing modifications `*p += 5`.
5. **Standard Output**: `printf` calling convention checking.