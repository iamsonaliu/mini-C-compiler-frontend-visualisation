import re

RESERVED = {
    'int', 'float', 'char', 'void',
    'if', 'else', 'while', 'for', 'do',
    'break', 'continue',
    'switch', 'case', 'default',
    'return', 'printf', 'scanf',
}

TOKEN_SPEC = [
    ('BLOCK_COMMENT',  r'/\*[\s\S]*?\*/'),
    ('LINE_COMMENT',   r'//[^\n]*'),
    ('NUMBER_FLOAT',   r'\d+\.\d+'),
    ('NUMBER_INT',     r'\d+'),
    ('CHAR_LITERAL',   r"'(\\.|[^'\\])'"),
    ('STRING_LITERAL', r'"(\\.|[^"\\])*"'),
    ('INCREMENT',      r'\+\+'),
    ('DECREMENT',      r'--'),
    ('PLUS_ASSIGN',    r'\+='),
    ('MINUS_ASSIGN',   r'-='),
    ('TIMES_ASSIGN',   r'\*='),
    ('DIVIDE_ASSIGN',  r'/='),
    ('MODULO_ASSIGN',  r'%='),
    ('ARROW',          r'->'),
    ('LEQ',            r'<='),
    ('GEQ',            r'>='),
    ('EQ',             r'=='),
    ('NEQ',            r'!='),
    ('AND',            r'&&'),
    ('OR',             r'\|\|'),
    ('AMPERSAND',      r'&'),
    ('ASSIGN',         r'='),
    ('PLUS',           r'\+'),
    ('MINUS',          r'-'),
    ('TIMES',          r'\*'),
    ('DIVIDE',         r'/'),
    ('MODULO',         r'%'),
    ('LT',             r'<'),
    ('GT',             r'>'),
    ('NOT',            r'!'),
    ('LPAREN',         r'\('),
    ('RPAREN',         r'\)'),
    ('LBRACE',         r'\{'),
    ('RBRACE',         r'\}'),
    ('LBRACKET',       r'\['),
    ('RBRACKET',       r'\]'),
    ('SEMI',           r';'),
    ('COLON',          r':'),
    ('COMMA',          r','),
    ('ID',             r'[A-Za-z_]\w*'),
    ('NEWLINE',        r'\n'),
    ('SKIP',           r'[ \t\r]+'),
    ('MISMATCH',       r'.'),
]

MASTER_RE = re.compile(
    '|'.join(f'(?P<{name}>{pat})' for name, pat in TOKEN_SPEC),
    re.DOTALL
)

def tokenize(code: str):
    tokens = []
    errors = []
    line = 1

    for m in MASTER_RE.finditer(code):
        kind  = m.lastgroup
        value = m.group()

        if kind in ('SKIP', 'LINE_COMMENT'):
            continue
        elif kind == 'BLOCK_COMMENT':
            line += value.count('\n')
            continue
        elif kind == 'NEWLINE':
            line += 1
            continue
        elif kind == 'MISMATCH':
            errors.append({
                'type': 'LEXICAL_ERROR',
                'value': value,
                'line': line,
                'message': f"Illegal character '{value}' at line {line}"
            })
            continue

        if kind == 'ID' and value in RESERVED:
            kind = value.upper()

        display = value
        if kind == 'CHAR_LITERAL':
            display = value[1:-1]
        elif kind == 'STRING_LITERAL':
            display = value[1:-1]

        tokens.append({'type': kind, 'value': display, 'line': line})

    return tokens, errors
