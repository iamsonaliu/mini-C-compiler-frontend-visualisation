import json

class ParseTreeNode:
    """Represents a node in the parse tree."""
    
    def __init__(self, node_type, value=None, line=None):
        self.node_type = node_type  # e.g., 'Program', 'Declaration', 'Expression'
        self.value = value          # Terminal value (for leaves)
        self.line = line            # Source line number
        self.children = []          # Child nodes
        self.metadata = {}          # Rich metadata
    
    def add_child(self, child):
        if child is not None:
            self.children.append(child)
        return self
    
    def to_dict(self):
        """Convert to dict for JSON serialization (D3.js compatible)."""
        node = {
            'name': self._get_display_name(),
            'type': self.node_type,
            'line': self.line,
            'ast_type': self._get_ast_type(),
            'metadata': self.metadata,
        }
        if self.children:
            node['children'] = [c.to_dict() for c in self.children]
        return node
    
    def _get_ast_type(self):
        t = self.node_type
        if t in ('ForStatement', 'WhileStatement', 'DoWhileStatement'):
            return 'loop'
        if t in ('FunctionDecl', 'FunctionCall', 'ParamList', 'Param'):
            return 'function'
        if t in ('IfStatement', 'SwitchStatement', 'CaseClause', 'DefaultClause'):
            return 'branch'
        if t in ('Declaration', 'Type'):
            return 'declaration'
        if t in ('Assignment', 'CompoundAssignment'):
            return 'assignment'
        if t in ('ReturnStatement', 'BreakStatement', 'ContinueStatement', 'PrintfStatement', 'ScanfStatement', 'ExpressionStatement'):
            return 'statement'
        if t in ('BinaryOp', 'UnaryOp', 'PrefixOp', 'PostfixOp', 'GroupedExpr', 'Identifier', 'IntLiteral', 'FloatLiteral', 'CharLiteral', 'StringLiteral', 'SubscriptExpr'):
            return 'expression'
        return 'other'

    def _get_display_name(self):
        if self.value is not None:
            return f"{self.node_type}: {self.value}"
        return self.node_type
    
    def __repr__(self):
        return f"ParseTreeNode({self.node_type}, {self.value})"