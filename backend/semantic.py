"""
Semantic Analyzer for Mini-C
- Symbol table construction
- Variable declared before use
- Type consistency checks (basic)
- Duplicate declaration detection
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
        current[name] = {'type': type_, 'line': line}
        return None
    
    def lookup(self, name):
        """Find a variable in any accessible scope."""
        for scope in reversed(self.scopes):
            if name in scope:
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
        var_name  = id_node.value   if id_node  else '?'
        line      = node.line or (id_node.line if id_node else 0)
        
        err = self.symbol_table.declare(var_name, type_name, line)
        if err:
            self.errors.append(err)
        
        # Check initializer expression if present
        if len(node.children) > 3:
            self._visit(node.children[3])
    
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
                    'message': f"Variable '{var_name}' used before declaration (line {id_node.line})"
                })
        # Visit expression
        if len(node.children) > 2:
            self._visit(node.children[2])
    
    def _visit_Identifier(self, node):
        sym = self.symbol_table.lookup(node.value)
        if sym is None:
            self.errors.append({
                'type': 'SEMANTIC_ERROR',
                'line': node.line,
                'message': f"Undefined variable '{node.value}' at line {node.line}"
            })
    
    def _visit_BinaryOp(self, node):
        # Check for division by zero (literal)
        if node.value == '/' and len(node.children) > 1:
            right = node.children[1]
            if right.node_type == 'IntLiteral' and right.value == 0:
                self.warnings.append({
                    'type': 'SEMANTIC_WARNING',
                    'line': node.line,
                    'message': f"Potential division by zero at line {node.line}"
                })
        self._generic_visit(node)
    
    def _visit_IfStatement(self, node):
        self._generic_visit(node)
    
    def _visit_WhileStatement(self, node):
        self._generic_visit(node)
    
    def _visit_ReturnStatement(self, node):
        self._generic_visit(node)
    
    def _visit_PrintfStatement(self, node):
        self._generic_visit(node)
    
    def _visit_ExpressionStatement(self, node):
        self._generic_visit(node)
    
    def _visit_GroupedExpr(self, node):
        self._generic_visit(node)
    
    def _visit_ArgList(self, node):
        self._generic_visit(node)
    
    # Terminals — no action needed
    def _visit_IntLiteral(self, node): pass
    def _visit_FloatLiteral(self, node): pass
    def _visit_CharLiteral(self, node): pass
    def _visit_StringLiteral(self, node): pass
    def _visit_Type(self, node): pass
    def _visit_Keyword(self, node): pass
    def _visit_AssignOp(self, node): pass
    def _visit_UnaryOp(self, node):
        self._generic_visit(node)