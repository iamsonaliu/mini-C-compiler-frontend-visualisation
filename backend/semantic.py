"""
Enhanced Semantic Analyzer for Mini-C
- Symbol table construction with Scope Tracking
- Variable declared before use detection
- Duplicate declaration detection
- NEW: Unused variable detection (Warnings)
- NEW: Basic Type consistency checks (Warnings)
"""

from parse_tree import ParseTreeNode

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # stack of scopes; index 0 = global
    
    def enter_scope(self):
        self.scopes.append({})
    
    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
    
    def declare(self, name, type_, line):
        """Declare a variable in the current scope. Returns error dict or None."""
        current = self.scopes[-1]
        if name in current:
            return {
                'type': 'SEMANTIC_ERROR',
                'line': line,
                'message': f"Variable '{name}' already declared in this scope (line {current[name]['line']})"
            }
        # Added 'used' flag to track if the variable is ever referenced
        current[name] = {'type': type_, 'line': line, 'used': False}
        return None
    
    def lookup(self, name):
        """Find a variable in any accessible scope and mark it as used."""
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name]['used'] = True # Mark as used when referenced
                return scope[name]
        return None
    
    def all_symbols(self):
        """Return all symbols across all scopes for display."""
        result = []
        for i, scope in enumerate(self.scopes):
            scope_name = 'global' if i == 0 else f'scope_{i}'
            for name, info in scope.items():
                result.append({
                    'name': name,
                    'type': info['type'],
                    'scope': scope_name,
                    'line': info['line']
                })
        return result


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []
    
    def analyze(self, tree):
        if tree is None:
            return [], [], []
        
        self._visit(tree)

        # NEW: Check for unused variables after the walk is complete
        for i, scope in enumerate(self.symbol_table.scopes):
            for name, info in scope.items():
                if not info['used']:
                    self.warnings.append({
                        'type': 'SEMANTIC_WARNING',
                        'line': info['line'],
                        'message': f"Variable '{name}' is declared but never used"
                    })

        return self.errors, self.warnings, self.symbol_table.all_symbols()
    
    def _visit(self, node):
        if node is None:
            return None
        
        method = f'_visit_{node.node_type}'
        visitor = getattr(self, method, self._generic_visit)
        return visitor(node)
    
    def _generic_visit(self, node):
        for child in node.children:
            self._visit(child)
    
    def _visit_Program(self, node):
        self._generic_visit(node)
    
    def _visit_StatementList(self, node):
        self._generic_visit(node)
    
    def _visit_Block(self, node):
        self.symbol_table.enter_scope()
        self._generic_visit(node)
        self.symbol_table.exit_scope()
    
    def _visit_Declaration(self, node):
        # children: Type, Identifier, [AssignOp, Expression]
        type_node = node.children[0] if len(node.children) > 0 else None
        id_node   = node.children[1] if len(node.children) > 1 else None
        
        type_name = type_node.value if type_node else 'unknown'
        var_name  = id_node.value   if id_node   else '?'
        line      = node.line or (id_node.line if id_node else 0)
        
        err = self.symbol_table.declare(var_name, type_name, line)
        if err:
            self.errors.append(err)
        
        # Check for type mismatch on initialization
        if len(node.children) > 3:
            expr_type = self._visit(node.children[3])
            if expr_type and type_name != expr_type:
                 self.warnings.append({
                    'type': 'SEMANTIC_WARNING',
                    'line': line,
                    'message': f"Type mismatch: Initializing {type_name} with {expr_type}"
                })
    
    def _visit_Assignment(self, node):
        # children: Identifier, AssignOp, Expression
        id_node = node.children[0] if node.children else None
        if id_node:
            var_name = id_node.value
            sym = self.symbol_table.lookup(var_name)
            if sym is None:
                self.errors.append({
                    'type': 'SEMANTIC_ERROR',
                    'line': id_node.line,
                    'message': f"Variable '{var_name}' used before declaration at line {id_node.line}"
                })
            else:
                # Check for type mismatch on assignment
                if len(node.children) > 2:
                    expr_type = self._visit(node.children[2])
                    if expr_type and sym['type'] != expr_type:
                        self.warnings.append({
                            'type': 'SEMANTIC_WARNING',
                            'line': id_node.line,
                            'message': f"Type mismatch: Assigning {expr_type} to {sym['type']} variable '{var_name}'"
                        })
    
    def _visit_Identifier(self, node):
        sym = self.symbol_table.lookup(node.value)
        if sym is None:
            self.errors.append({
                'type': 'SEMANTIC_ERROR',
                'line': node.line,
                'message': f"Undefined variable '{node.value}' at line {node.line}"
            })
            return 'unknown'
        return sym['type']
    
    def _visit_BinaryOp(self, node):
        # Check for division by zero
        if node.value == '/' and len(node.children) > 1:
            right = node.children[1]
            if right.node_type == 'IntLiteral' and str(right.value) == '0':
                self.warnings.append({
                    'type': 'SEMANTIC_WARNING',
                    'line': node.line,
                    'message': f"Potential division by zero at line {node.line}"
                })
        
        # Binary ops in Mini-C usually result in the type of the first operand
        left_type = self._visit(node.children[0]) if len(node.children) > 0 else None
        self._visit(node.children[1]) if len(node.children) > 1 else None
        return left_type
    
    def _visit_IntLiteral(self, node): return 'int'
    def _visit_FloatLiteral(self, node): return 'float'
    def _visit_CharLiteral(self, node): return 'char'
    def _visit_StringLiteral(self, node): return 'string'

    def _visit_IfStatement(self, node): self._generic_visit(node)
    def _visit_WhileStatement(self, node): self._generic_visit(node)
    def _visit_ReturnStatement(self, node): self._generic_visit(node)
    def _visit_PrintfStatement(self, node): self._generic_visit(node)
    def _visit_ExpressionStatement(self, node): self._generic_visit(node)
    def _visit_GroupedExpr(self, node): return self._visit(node.children[0]) if node.children else None
    def _visit_ArgList(self, node): self._generic_visit(node)
    def _visit_Type(self, node): pass
    def _visit_Keyword(self, node): pass
    def _visit_AssignOp(self, node): pass
    def _visit_UnaryOp(self, node): return self._visit(node.children[0]) if node.children else None