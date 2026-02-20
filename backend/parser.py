"""
Pure-Python recursive-descent parser for Mini-C.
Builds a ParseTreeNode tree and collects syntax errors.
"""

from parse_tree import ParseTreeNode
from lexer import tokenize

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

    # ── Helpers ───────────────────────────────────────────────────────────────
    def peek(self):
        while self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek_type(self):
        t = self.peek()
        return t['type'] if t else None

    def consume(self, expected_type=None):
        t = self.peek()
        if t is None:
            if expected_type:
                self.errors.append({
                    'type': 'SYNTAX_ERROR', 'line': '?', 'value': 'EOF',
                    'message': f"Expected '{expected_type}' but reached end of input"
                })
            return None
        if expected_type and t['type'] != expected_type:
            self.errors.append({
                'type': 'SYNTAX_ERROR', 'line': t['line'], 'value': t['value'],
                'message': f"Expected '{expected_type}' but found '{t['value']}' at line {t['line']}"
            })
            return None
        self.pos += 1
        return t

    def match(self, *types):
        return self.peek_type() in types

    def expect(self, typ):
        t = self.consume(typ)
        return t

    def sync(self):
        """Error recovery: skip to next semicolon or closing brace."""
        while self.peek() and self.peek_type() not in ('SEMI', 'RBRACE'):
            self.pos += 1
        if self.peek_type() == 'SEMI':
            self.pos += 1

    # ── Grammar ───────────────────────────────────────────────────────────────
    TYPE_TOKENS = ('INT', 'FLOAT', 'CHAR', 'VOID')

    def parse_program(self):
        node = ParseTreeNode('Program')
        sl = self.parse_statement_list()
        node.add_child(sl)
        return node

    def parse_statement_list(self):
        node = ParseTreeNode('StatementList')
        while self.peek() and not self.match('RBRACE'):
            stmt = self.parse_statement()
            if stmt:
                node.add_child(stmt)
        return node

    def parse_statement(self):
        t = self.peek()
        if t is None:
            return None
        kind = t['type']

        if kind in self.TYPE_TOKENS:
            return self.parse_declaration()
        elif kind == 'IF':
            return self.parse_if()
        elif kind == 'WHILE':
            return self.parse_while()
        elif kind == 'RETURN':
            return self.parse_return()
        elif kind == 'PRINTF':
            return self.parse_printf()
        elif kind == 'LBRACE':
            return self.parse_block()
        elif kind == 'ID':
            return self.parse_assignment_or_expr()
        else:
            # Expression statement or unknown
            return self.parse_expr_stmt()

    def parse_declaration(self):
        node = ParseTreeNode('Declaration')
        type_tok = self.consume()
        node.line = type_tok['line']
        node.add_child(ParseTreeNode('Type', type_tok['value'], type_tok['line']))

        id_tok = self.expect('ID')
        if id_tok:
            node.add_child(ParseTreeNode('Identifier', id_tok['value'], id_tok['line']))

        if self.match('ASSIGN'):
            self.consume()
            node.add_child(ParseTreeNode('AssignOp', '='))
            expr = self.parse_expression()
            node.add_child(expr)

        if not self.expect('SEMI'):
            self.sync()
        return node

    def parse_assignment_or_expr(self):
        # Look ahead: ID ASSIGN = assignment, else expr stmt
        if (self.pos + 1 < len(self.tokens) and
                self.tokens[self.pos + 1]['type'] == 'ASSIGN'):
            return self.parse_assignment()
        return self.parse_expr_stmt()

    def parse_assignment(self):
        node = ParseTreeNode('Assignment')
        id_tok = self.consume()
        node.line = id_tok['line']
        node.add_child(ParseTreeNode('Identifier', id_tok['value'], id_tok['line']))
        self.consume('ASSIGN')
        node.add_child(ParseTreeNode('AssignOp', '='))
        expr = self.parse_expression()
        node.add_child(expr)
        if not self.expect('SEMI'):
            self.sync()
        return node

    def parse_if(self):
        node = ParseTreeNode('IfStatement')
        tok = self.consume('IF')
        node.line = tok['line'] if tok else None
        node.add_child(ParseTreeNode('Keyword', 'if', node.line))
        self.expect('LPAREN')
        cond = self.parse_expression()
        node.add_child(cond)
        self.expect('RPAREN')
        body = self.parse_block()
        node.add_child(body)
        if self.match('ELSE'):
            self.consume()
            node.add_child(ParseTreeNode('Keyword', 'else'))
            else_body = self.parse_block()
            node.add_child(else_body)
        return node

    def parse_while(self):
        node = ParseTreeNode('WhileStatement')
        tok = self.consume('WHILE')
        node.line = tok['line'] if tok else None
        node.add_child(ParseTreeNode('Keyword', 'while', node.line))
        self.expect('LPAREN')
        cond = self.parse_expression()
        node.add_child(cond)
        self.expect('RPAREN')
        body = self.parse_block()
        node.add_child(body)
        return node

    def parse_return(self):
        node = ParseTreeNode('ReturnStatement')
        tok = self.consume('RETURN')
        node.line = tok['line'] if tok else None
        node.add_child(ParseTreeNode('Keyword', 'return', node.line))
        if not self.match('SEMI'):
            expr = self.parse_expression()
            node.add_child(expr)
        self.expect('SEMI')
        return node

    def parse_printf(self):
        node = ParseTreeNode('PrintfStatement')
        tok = self.consume('PRINTF')
        node.line = tok['line'] if tok else None
        self.expect('LPAREN')
        args = self.parse_arg_list()
        node.add_child(args)
        self.expect('RPAREN')
        if not self.expect('SEMI'):
            self.sync()
        return node

    def parse_arg_list(self):
        node = ParseTreeNode('ArgList')
        if not self.match('RPAREN'):
            node.add_child(self.parse_expression())
            while self.match('COMMA'):
                self.consume()
                node.add_child(self.parse_expression())
        return node

    def parse_block(self):
        node = ParseTreeNode('Block')
        tok = self.expect('LBRACE')
        node.line = tok['line'] if tok else None
        if not self.match('RBRACE'):
            sl = self.parse_statement_list()
            node.add_child(sl)
        self.expect('RBRACE')
        return node

    def parse_expr_stmt(self):
        node = ParseTreeNode('ExpressionStatement')
        expr = self.parse_expression()
        node.add_child(expr)
        if not self.expect('SEMI'):
            self.sync()
        return node

    # ── Expressions (Pratt / precedence climbing) ─────────────────────────────
    PREC = {
        'OR': 1, 'AND': 2,
        'EQ': 3, 'NEQ': 3,
        'LT': 4, 'GT': 4, 'LEQ': 4, 'GEQ': 4,
        'PLUS': 5, 'MINUS': 5,
        'TIMES': 6, 'DIVIDE': 6, 'MODULO': 6,
    }

    def parse_expression(self, min_prec=0):
        left = self.parse_unary()
        while True:
            op = self.peek()
            if op is None or op['type'] not in self.PREC:
                break
            prec = self.PREC[op['type']]
            if prec <= min_prec:
                break
            self.consume()
            right = self.parse_expression(prec)
            node = ParseTreeNode('BinaryOp', op['value'], op['line'])
            node.add_child(left)
            node.add_child(right)
            left = node
        return left

    def parse_unary(self):
        if self.match('NOT'):
            tok = self.consume()
            node = ParseTreeNode('UnaryOp', '!', tok['line'])
            node.add_child(self.parse_unary())
            return node
        if self.match('MINUS'):
            tok = self.consume()
            node = ParseTreeNode('UnaryOp', '-', tok['line'])
            node.add_child(self.parse_unary())
            return node
        return self.parse_primary()

    def parse_primary(self):
        t = self.peek()
        if t is None:
            self.errors.append({
                'type': 'SYNTAX_ERROR', 'line': '?', 'value': 'EOF',
                'message': "Unexpected end of input in expression"
            })
            return ParseTreeNode('Error', 'EOF')

        kind = t['type']

        if kind == 'LPAREN':
            self.consume()
            node = ParseTreeNode('GroupedExpr')
            node.add_child(self.parse_expression())
            self.expect('RPAREN')
            return node
        elif kind == 'NUMBER_INT':
            self.consume()
            return ParseTreeNode('IntLiteral', t['value'], t['line'])
        elif kind == 'NUMBER_FLOAT':
            self.consume()
            return ParseTreeNode('FloatLiteral', t['value'], t['line'])
        elif kind == 'CHAR_LITERAL':
            self.consume()
            return ParseTreeNode('CharLiteral', t['value'], t['line'])
        elif kind == 'STRING_LITERAL':
            self.consume()
            return ParseTreeNode('StringLiteral', t['value'], t['line'])
        elif kind == 'ID':
            self.consume()
            return ParseTreeNode('Identifier', t['value'], t['line'])
        else:
            self.errors.append({
                'type': 'SYNTAX_ERROR', 'line': t['line'], 'value': t['value'],
                'message': f"Unexpected token '{t['value']}' at line {t['line']}"
            })
            self.pos += 1
            return ParseTreeNode('Error', t['value'], t['line'])


def parse(code: str):
    tokens, lex_errors = tokenize(code)
    # Filter out lex error tokens so parser gets clean stream
    clean_tokens = [t for t in tokens]
    p = Parser(clean_tokens)
    tree = p.parse_program()
    return tree, p.errors, lex_errors