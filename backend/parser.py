"""
Pure-Python recursive-descent parser for Mini-C.
Builds a ParseTreeNode tree and collects syntax errors.

Supported constructs:
  - Variable declarations & assignments (including compound: +=, -=, *=, /=)
  - if / else
  - while, for, do-while loops
  - break, continue
  - switch / case / default
  - return, printf, scanf
  - Function definitions & function calls
  - Increment / decrement (prefix & postfix)
  - Full expression parsing with precedence climbing
"""

from parse_tree import ParseTreeNode
from lexer import tokenize

# ── Compound-assignment token set ────────────────────────────────────────────
COMPOUND_ASSIGN_OPS = {'PLUS_ASSIGN', 'MINUS_ASSIGN', 'TIMES_ASSIGN', 'DIVIDE_ASSIGN'}


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

    def lookahead(self, offset=1):
        """Return the token at pos+offset (or None)."""
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

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
            # Could be a function definition:  type ID (
            la1 = self.lookahead(1)
            la2 = self.lookahead(2)
            if (la1 and la1['type'] == 'ID' and
                    la2 and la2['type'] == 'LPAREN'):
                return self.parse_function_def()
            return self.parse_declaration()
        elif kind == 'IF':
            return self.parse_if()
        elif kind == 'WHILE':
            return self.parse_while()
        elif kind == 'FOR':
            return self.parse_for()
        elif kind == 'DO':
            return self.parse_do_while()
        elif kind == 'SWITCH':
            return self.parse_switch()
        elif kind == 'BREAK':
            return self.parse_break()
        elif kind == 'CONTINUE':
            return self.parse_continue()
        elif kind == 'RETURN':
            return self.parse_return()
        elif kind == 'PRINTF':
            return self.parse_printf()
        elif kind == 'SCANF':
            return self.parse_scanf()
        elif kind == 'LBRACE':
            return self.parse_block()
        elif kind == 'ID':
            return self.parse_assignment_or_expr()
        elif kind in ('INCREMENT', 'DECREMENT'):
            return self.parse_expr_stmt()
        else:
            # Expression statement or unknown
            return self.parse_expr_stmt()

    # ── Declarations ──────────────────────────────────────────────────────────
    def parse_declaration(self):
        node = ParseTreeNode('Declaration')
        type_tok = self.consume()
        node.line = type_tok['line']
        type_val = type_tok['value']
        if self.match('TIMES'):
            self.consume()
            type_val += '*'
        node.add_child(ParseTreeNode('Type', type_val, type_tok['line']))

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

    # ── Assignments (simple + compound) ───────────────────────────────────────
    def parse_assignment_or_expr(self):
        la = self.lookahead(1)
        if la and la['type'] == 'ASSIGN':
            return self.parse_assignment()
        if la and la['type'] in COMPOUND_ASSIGN_OPS:
            return self.parse_compound_assignment()
        if la and la['type'] in ('INCREMENT', 'DECREMENT'):
            return self.parse_postfix_stmt()
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

    def parse_compound_assignment(self):
        node = ParseTreeNode('CompoundAssignment')
        id_tok = self.consume()
        node.line = id_tok['line']
        node.add_child(ParseTreeNode('Identifier', id_tok['value'], id_tok['line']))
        op_tok = self.consume()  # +=, -=, *=, /=
        node.add_child(ParseTreeNode('CompoundOp', op_tok['value'], op_tok['line']))
        expr = self.parse_expression()
        node.add_child(expr)
        if not self.expect('SEMI'):
            self.sync()
        return node

    def parse_postfix_stmt(self):
        """Handle standalone `i++;` or `i--;` as a statement."""
        node = ParseTreeNode('PostfixStatement')
        id_tok = self.consume()
        node.line = id_tok['line']
        node.add_child(ParseTreeNode('Identifier', id_tok['value'], id_tok['line']))
        op_tok = self.consume()  # ++ or --
        op_val = '++' if op_tok['type'] == 'INCREMENT' else '--'
        node.add_child(ParseTreeNode('PostfixOp', op_val, op_tok['line']))
        if not self.expect('SEMI'):
            self.sync()
        return node

    # ── Control Flow ──────────────────────────────────────────────────────────
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
            if self.match('IF'):
                # else if chain
                else_body = self.parse_if()
            else:
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

    def parse_for(self):
        node = ParseTreeNode('ForStatement')
        tok = self.consume('FOR')
        node.line = tok['line'] if tok else None
        node.add_child(ParseTreeNode('Keyword', 'for', node.line))
        self.expect('LPAREN')

        # ── Init clause ──────────────────────────────────────────────────
        init_node = ParseTreeNode('ForInit')
        if self.match('SEMI'):
            # Empty init
            pass
        elif self.match(*self.TYPE_TOKENS):
            init_node.add_child(self._parse_for_declaration())
        else:
            init_node.add_child(self._parse_for_assign_or_expr())
        node.add_child(init_node)
        self.expect('SEMI')

        # ── Condition clause ─────────────────────────────────────────────
        cond_node = ParseTreeNode('ForCondition')
        if not self.match('SEMI'):
            cond_node.add_child(self.parse_expression())
        node.add_child(cond_node)
        self.expect('SEMI')

        # ── Update clause ────────────────────────────────────────────────
        update_node = ParseTreeNode('ForUpdate')
        if not self.match('RPAREN'):
            update_node.add_child(self._parse_for_update_expr())
        node.add_child(update_node)
        self.expect('RPAREN')

        body = self.parse_block()
        node.add_child(body)
        return node

    def _parse_for_declaration(self):
        """Parse a declaration inside for-init (no trailing semicolon)."""
        node = ParseTreeNode('Declaration')
        type_tok = self.consume()
        node.line = type_tok['line']
        type_val = type_tok['value']
        if self.match('TIMES'):
            self.consume()
            type_val += '*'
        node.add_child(ParseTreeNode('Type', type_val, type_tok['line']))
        id_tok = self.expect('ID')
        if id_tok:
            node.add_child(ParseTreeNode('Identifier', id_tok['value'], id_tok['line']))
        if self.match('ASSIGN'):
            self.consume()
            node.add_child(ParseTreeNode('AssignOp', '='))
            expr = self.parse_expression()
            node.add_child(expr)
        return node

    def _parse_for_assign_or_expr(self):
        """Parse assignment or expression in for-init (no trailing semicolon)."""
        la = self.lookahead(1)
        if la and la['type'] == 'ASSIGN':
            node = ParseTreeNode('Assignment')
            id_tok = self.consume()
            node.line = id_tok['line']
            node.add_child(ParseTreeNode('Identifier', id_tok['value'], id_tok['line']))
            self.consume('ASSIGN')
            node.add_child(ParseTreeNode('AssignOp', '='))
            expr = self.parse_expression()
            node.add_child(expr)
            return node
        return self.parse_expression()

    def _parse_for_update_expr(self):
        """Parse the update expression in a for-loop (no trailing semicolon).
        Handles: i++, i--, ++i, --i, i += expr, i = expr, or general expr.
        """
        # Prefix ++ / --
        if self.match('INCREMENT', 'DECREMENT'):
            op_tok = self.consume()
            op_val = '++' if op_tok['type'] == 'INCREMENT' else '--'
            node = ParseTreeNode('PrefixOp', op_val, op_tok['line'])
            operand = self.parse_unary()
            node.add_child(operand)
            return node

        # ID-based updates
        if self.match('ID'):
            la = self.lookahead(1)
            if la and la['type'] in ('INCREMENT', 'DECREMENT'):
                # Postfix
                id_tok = self.consume()
                op_tok = self.consume()
                op_val = '++' if op_tok['type'] == 'INCREMENT' else '--'
                node = ParseTreeNode('PostfixOp', op_val, op_tok['line'])
                node.add_child(ParseTreeNode('Identifier', id_tok['value'], id_tok['line']))
                return node
            if la and la['type'] == 'ASSIGN':
                node = ParseTreeNode('Assignment')
                id_tok = self.consume()
                node.line = id_tok['line']
                node.add_child(ParseTreeNode('Identifier', id_tok['value'], id_tok['line']))
                self.consume('ASSIGN')
                node.add_child(ParseTreeNode('AssignOp', '='))
                expr = self.parse_expression()
                node.add_child(expr)
                return node
            if la and la['type'] in COMPOUND_ASSIGN_OPS:
                node = ParseTreeNode('CompoundAssignment')
                id_tok = self.consume()
                node.line = id_tok['line']
                node.add_child(ParseTreeNode('Identifier', id_tok['value'], id_tok['line']))
                op_tok = self.consume()
                node.add_child(ParseTreeNode('CompoundOp', op_tok['value'], op_tok['line']))
                expr = self.parse_expression()
                node.add_child(expr)
                return node

        return self.parse_expression()

    def parse_do_while(self):
        node = ParseTreeNode('DoWhileStatement')
        tok = self.consume('DO')
        node.line = tok['line'] if tok else None
        node.add_child(ParseTreeNode('Keyword', 'do', node.line))
        body = self.parse_block()
        node.add_child(body)
        self.expect('WHILE')
        node.add_child(ParseTreeNode('Keyword', 'while'))
        self.expect('LPAREN')
        cond = self.parse_expression()
        node.add_child(cond)
        self.expect('RPAREN')
        if not self.expect('SEMI'):
            self.sync()
        return node

    def parse_switch(self):
        node = ParseTreeNode('SwitchStatement')
        tok = self.consume('SWITCH')
        node.line = tok['line'] if tok else None
        node.add_child(ParseTreeNode('Keyword', 'switch', node.line))
        self.expect('LPAREN')
        expr = self.parse_expression()
        node.add_child(expr)
        self.expect('RPAREN')
        self.expect('LBRACE')

        while self.peek() and not self.match('RBRACE'):
            if self.match('CASE'):
                node.add_child(self.parse_case_clause())
            elif self.match('DEFAULT'):
                node.add_child(self.parse_default_clause())
            else:
                # Error recovery
                self.errors.append({
                    'type': 'SYNTAX_ERROR',
                    'line': self.peek()['line'],
                    'value': self.peek()['value'],
                    'message': f"Expected 'case' or 'default' in switch block at line {self.peek()['line']}"
                })
                self.pos += 1

        self.expect('RBRACE')
        return node

    def parse_case_clause(self):
        node = ParseTreeNode('CaseClause')
        tok = self.consume('CASE')
        node.line = tok['line'] if tok else None
        node.add_child(ParseTreeNode('Keyword', 'case', node.line))
        expr = self.parse_expression()
        node.add_child(expr)
        self.expect('COLON')

        # Parse statements until next case / default / }
        stmts = ParseTreeNode('StatementList')
        while (self.peek() and
               not self.match('CASE', 'DEFAULT', 'RBRACE')):
            s = self.parse_statement()
            if s:
                stmts.add_child(s)
        node.add_child(stmts)
        return node

    def parse_default_clause(self):
        node = ParseTreeNode('DefaultClause')
        tok = self.consume('DEFAULT')
        node.line = tok['line'] if tok else None
        node.add_child(ParseTreeNode('Keyword', 'default', node.line))
        self.expect('COLON')

        stmts = ParseTreeNode('StatementList')
        while (self.peek() and
               not self.match('CASE', 'DEFAULT', 'RBRACE')):
            s = self.parse_statement()
            if s:
                stmts.add_child(s)
        node.add_child(stmts)
        return node

    def parse_break(self):
        node = ParseTreeNode('BreakStatement')
        tok = self.consume('BREAK')
        node.line = tok['line'] if tok else None
        node.add_child(ParseTreeNode('Keyword', 'break', node.line))
        if not self.expect('SEMI'):
            self.sync()
        return node

    def parse_continue(self):
        node = ParseTreeNode('ContinueStatement')
        tok = self.consume('CONTINUE')
        node.line = tok['line'] if tok else None
        node.add_child(ParseTreeNode('Keyword', 'continue', node.line))
        if not self.expect('SEMI'):
            self.sync()
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

    def parse_scanf(self):
        node = ParseTreeNode('ScanfStatement')
        tok = self.consume('SCANF')
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

    # ── Function definitions ──────────────────────────────────────────────────
    def parse_function_def(self):
        node = ParseTreeNode('FunctionDecl')
        type_tok = self.consume()
        node.line = type_tok['line']
        type_val = type_tok['value']
        if self.match('TIMES'):
            self.consume()
            type_val += '*'
        node.add_child(ParseTreeNode('Type', type_val, type_tok['line']))

        id_tok = self.expect('ID')
        if id_tok:
            node.add_child(ParseTreeNode('Identifier', id_tok['value'], id_tok['line']))

        self.expect('LPAREN')
        params = self.parse_param_list()
        node.add_child(params)
        self.expect('RPAREN')

        body = self.parse_block()
        node.add_child(body)
        return node

    def parse_param_list(self):
        node = ParseTreeNode('ParamList')
        if not self.match('RPAREN'):
            node.add_child(self.parse_param())
            while self.match('COMMA'):
                self.consume()
                node.add_child(self.parse_param())
        return node

    def parse_param(self):
        node = ParseTreeNode('Param')
        type_tok = self.consume()
        if type_tok:
            node.line = type_tok['line']
            type_val = type_tok['value']
            if self.match('TIMES'):
                self.consume()
                type_val += '*'
            node.add_child(ParseTreeNode('Type', type_val, type_tok['line']))
        id_tok = self.expect('ID')
        if id_tok:
            node.add_child(ParseTreeNode('Identifier', id_tok['value'], id_tok['line']))
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
        if self.match('TIMES'):
            tok = self.consume()
            node = ParseTreeNode('UnaryOp', '*', tok['line'])
            node.add_child(self.parse_unary())
            return node
        if self.match('AMPERSAND'):
            tok = self.consume()
            node = ParseTreeNode('UnaryOp', '&', tok['line'])
            node.add_child(self.parse_unary())
            return node
        # Prefix increment / decrement
        if self.match('INCREMENT'):
            tok = self.consume()
            node = ParseTreeNode('PrefixOp', '++', tok['line'])
            node.add_child(self.parse_unary())
            return node
        if self.match('DECREMENT'):
            tok = self.consume()
            node = ParseTreeNode('PrefixOp', '--', tok['line'])
            node.add_child(self.parse_unary())
            return node
        return self.parse_postfix()

    def parse_postfix(self):
        """Parse postfix expressions: function calls, postfix ++ / --."""
        node = self.parse_primary()
        while True:
            if self.match('INCREMENT'):
                tok = self.consume()
                wrapper = ParseTreeNode('PostfixOp', '++', tok['line'])
                wrapper.add_child(node)
                node = wrapper
            elif self.match('DECREMENT'):
                tok = self.consume()
                wrapper = ParseTreeNode('PostfixOp', '--', tok['line'])
                wrapper.add_child(node)
                node = wrapper
            else:
                break
        return node

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
            # Check for function call: ID ( args )
            if self.match('LPAREN'):
                call_node = ParseTreeNode('FunctionCall', t['value'], t['line'])
                call_node.add_child(ParseTreeNode('Identifier', t['value'], t['line']))
                self.consume('LPAREN')
                args = self.parse_arg_list()
                call_node.add_child(args)
                self.expect('RPAREN')
                return call_node
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