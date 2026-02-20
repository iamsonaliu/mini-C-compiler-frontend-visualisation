import json

class ParseTreeNode:
    """Represents a node in the parse tree."""
    
    def __init__(self, node_type, value=None, line=None):
        self.node_type = node_type  # e.g., 'Program', 'Declaration', 'Expression'
        self.value = value          # Terminal value (for leaves)
        self.line = line            # Source line number
        self.children = []          # Child nodes
    
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
        }
        if self.children:
            node['children'] = [c.to_dict() for c in self.children]
        return node
    
    def _get_display_name(self):
        if self.value is not None:
            return f"{self.node_type}: {self.value}"
        return self.node_type
    
    def __repr__(self):
        return f"ParseTreeNode({self.node_type}, {self.value})"