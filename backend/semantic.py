"""
Enhanced Semantic Analyzer for Mini-C
- Symbol table construction with Scope Tracking
- Variable declared before use detection
- Duplicate declaration detection
- Unused variable detection (Warnings)
- Basic Type consistency checks (Warnings)
- Loop context tracking (break/continue validation)
- Function symbol tracking & call validation
- Return-type consistency checking
- Array subscript type checking
- Pointer address-of and dereference type synthesis
- Rich symbol metadata export for frontend
"""

from parse_tree import ParseTreeNode


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # stack of scopes; index 0 = global
        self.functions = {}  # name -> {return_type, params, line}
        self.all_tracked = []  # track all symbols even after scope exit

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(self, name, type_, line, array_dims=None, ptr_depth=0, param_names=None):
        """Declare a variable in the current scope. Returns error dict or None."""
        current = self.scopes[-1]
        if name in current:
            return {
                'type': 'SEMANTIC_ERROR',
                'line': line,
                'message': f"Variable '{name}' already declared in this scope (line {current[name]['line']})"
            }
        
        scope_name = 'global' if len(self.scopes) == 1 else f'scope_{len(self.scopes)-1}'
        info = {
            'name': name,
            'type': type_,
            'line': line,
            'used': False,
            'scope': scope_name,
            'array_dims': array_dims,
            'ptr_depth': ptr_depth,
            'params': param_names
        }
        current[name] = info
        self.all_tracked.append(info)
        return None

    def declare_function(self, name, return_type, param_count, line, param_names=None):
        """Declare a function. Returns error dict or None."""
        if name in self.functions:
            return {
                'type': 'SEMANTIC_ERROR',
                'line': line,
                'message': f"Function '{name}' already defined (line {self.functions[name]['line']})"
            }
            
        info = {
            'name': name + '()',
            'type': return_type,
            'return_type': return_type,
            'param_count': param_count,
            'line': line,
            'used': True,
            'scope': 'global',
            'array_dims': None,
            'ptr_depth': 0,
            'params': param_names
        }
        self.functions[name] = info
        self.all_tracked.append(info)
        return None

    def lookup_function(self, name):
        return self.functions.get(name)

    def lookup(self, name):
        """Find a variable in any accessible scope and mark it as used."""
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name]['used'] = True  # Mark as used when referenced
                return scope[name]
        return None

    def all_symbols(self):
        """Return all symbols across all scopes for display."""
        result = []
        for info in self.all_tracked:
            result.append({
                'name': info['name'],
                'type': info['type'],
                'scope': info['scope'],
                'line': info['line'],
                'used': info['used'],
                'array_dims': info.get('array_dims'),
                'ptr_depth': info.get('ptr_depth'),
                'params': info.get('params')
            })
        return result


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []
        self.loop_depth = 0      # Track nesting depth for break/continue
        self.switch_depth = 0    # Track switch nesting for break
        self.current_func = None # Track current active function

    def analyze(self, tree):
        if tree is None:
            return [], [], []

        self._visit(tree)

        # Check for unused variables after the walk is complete
        for info in self.symbol_table.all_tracked:
            if not info.get('used', True) and not info['name'].endswith('()'):
                self.warnings.append({
                    'type': 'SEMANTIC_WARNING',
                    'line': info['line'],
                    'message': f"Variable '{info['name']}' is declared but never used"
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

    # ── Top-level ─────────────────────────────────────────────────────────────
    def _visit_Program(self, node):
        self._generic_visit(node)

    def _visit_StatementList(self, node):
        self._generic_visit(node)

    def _visit_Block(self, node):
        self.symbol_table.enter_scope()
        self._generic_visit(node)
        self.symbol_table.exit_scope()

    # ── Declarations & Assignments ────────────────────────────────────────────
    def _visit_Declaration(self, node):
        # children: Type, Identifier, [AssignOp, Expression]
        type_node = node.children[0] if len(node.children) > 0 else None
        id_node   = node.children[1] if len(node.children) > 1 else None

        type_name = type_node.value if type_node else 'unknown'
        var_name  = id_node.value   if id_node   else '?'
        line      = node.line or (id_node.line if id_node else 0)

        # Parse array dimensions if present
        array_dims = None
        if id_node and id_node.children:
            for child in id_node.children:
                if child.node_type == 'ArraySize':
                    array_dims = child.value

        ptr_depth = type_name.count('*')

        err = self.symbol_table.declare(var_name, type_name, line, array_dims=array_dims, ptr_depth=ptr_depth)
        if err:
            self.errors.append(err)

        # Check for type mismatch on initialization
        if len(node.children) > 3:
            expr_type = self._visit(node.children[3])
            if expr_type and expr_type != 'unknown' and type_name != expr_type:
                 self.warnings.append({
                    'type': 'SEMANTIC_WARNING',
                    'line': line,
                    'message': f"Type mismatch: Initializing {type_name} with {expr_type}"
                })

    def _visit_Assignment(self, node):
        # children: Identifier, AssignOp, Expression
        lhs_node = node.children[0] if node.children else None
        lhs_type = 'unknown'
        if lhs_node:
            lhs_type = self._visit(lhs_node)

        # Visit RHS expression
        if len(node.children) > 2:
            rhs_type = self._visit(node.children[2])
            if lhs_type and lhs_type != 'unknown' and rhs_type and rhs_type != 'unknown' and lhs_type != rhs_type:
                self.warnings.append({
                    'type': 'SEMANTIC_WARNING',
                    'line': lhs_node.line if lhs_node else 0,
                    'message': f"Type mismatch: Assigning {rhs_type} to {lhs_type} variable"
                })

    def _visit_CompoundAssignment(self, node):
        # children: Identifier, CompoundOp, Expression
        lhs_node = node.children[0] if node.children else None
        if lhs_node:
            self._visit(lhs_node)
        # Visit the expression
        if len(node.children) > 2:
            self._visit(node.children[2])

    def _visit_PostfixStatement(self, node):
        lhs_node = node.children[0] if node.children else None
        if lhs_node:
            self._visit(lhs_node)

    # ── Expressions ───────────────────────────────────────────────────────────
    def _visit_Identifier(self, node):
        if self.symbol_table.lookup_function(node.value):
            return 'function'
        sym = self.symbol_table.lookup(node.value)
        if sym is None:
            self.errors.append({
                'type': 'SEMANTIC_ERROR',
                'line': node.line,
                'message': f"Undefined variable '{node.value}' at line {node.line}"
            })
            return 'unknown'
        return sym['type']

    def _visit_SubscriptExpr(self, node):
        # children: base identifier/expression, index expression
        arr_node = node.children[0] if len(node.children) > 0 else None
        idx_node = node.children[1] if len(node.children) > 1 else None
        
        arr_type = 'unknown'
        if arr_node:
            arr_type = self._visit(arr_node)
        if idx_node:
            idx_type = self._visit(idx_node)
            if idx_type and idx_type != 'int' and idx_type != 'unknown':
                self.warnings.append({
                    'type': 'SEMANTIC_WARNING',
                    'line': node.line,
                    'message': f"Array subscript expression at line {node.line} is of type '{idx_type}' instead of 'int'"
                })
        # If it is an array type (like 'int'), subscripting yields the base type
        return arr_type

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

    def _visit_UnaryOp(self, node):
        child_type = self._visit(node.children[0]) if node.children else 'unknown'
        if node.value == '&':
            return child_type + '*'
        if node.value == '*':
            if child_type.endswith('*'):
                return child_type[:-1]
            return child_type
        return child_type

    def _visit_PrefixOp(self, node):
        # ++i or --i  →  operand must be a declared variable
        if node.children:
            child = node.children[0]
            return self._visit(child)
        return None

    def _visit_PostfixOp(self, node):
        # i++ or i--  →  operand must be a declared variable
        if node.children:
            child = node.children[0]
            return self._visit(child)
        return None

    # ── Literals ──────────────────────────────────────────────────────────────
    def _visit_IntLiteral(self, node): return 'int'
    def _visit_FloatLiteral(self, node): return 'float'
    def _visit_CharLiteral(self, node): return 'char'
    def _visit_StringLiteral(self, node): return 'string'

    # ── Control Flow ──────────────────────────────────────────────────────────
    def _visit_IfStatement(self, node):
        self._generic_visit(node)

    def _visit_WhileStatement(self, node):
        self.loop_depth += 1
        self._generic_visit(node)
        self.loop_depth -= 1

    def _visit_ForStatement(self, node):
        self.loop_depth += 1
        # For loops create their own scope for the init variable
        self.symbol_table.enter_scope()
        self._generic_visit(node)
        self.symbol_table.exit_scope()
        self.loop_depth -= 1

    def _visit_ForInit(self, node):
        self._generic_visit(node)

    def _visit_ForCondition(self, node):
        self._generic_visit(node)

    def _visit_ForUpdate(self, node):
        self._generic_visit(node)

    def _visit_DoWhileStatement(self, node):
        self.loop_depth += 1
        self._generic_visit(node)
        self.loop_depth -= 1

    def _visit_SwitchStatement(self, node):
        self.switch_depth += 1
        self._generic_visit(node)
        self.switch_depth -= 1

    def _visit_CaseClause(self, node):
        self._generic_visit(node)

    def _visit_DefaultClause(self, node):
        self._generic_visit(node)

    def _visit_BreakStatement(self, node):
        if self.loop_depth == 0 and self.switch_depth == 0:
            self.errors.append({
                'type': 'SEMANTIC_ERROR',
                'line': node.line,
                'message': f"'break' statement not within a loop or switch at line {node.line}"
            })

    def _visit_ContinueStatement(self, node):
        if self.loop_depth == 0:
            self.errors.append({
                'type': 'SEMANTIC_ERROR',
                'line': node.line,
                'message': f"'continue' statement not within a loop at line {node.line}"
            })

    def _visit_ReturnStatement(self, node):
        ret_type = 'void'
        # child list contains Keyword(return), and optionally the returned expression
        if len(node.children) > 1:
            ret_type = self._visit(node.children[1])
        
        if self.current_func:
            expected_type = self.current_func['return_type']
            if expected_type == 'void' and ret_type != 'void':
                self.errors.append({
                    'type': 'SEMANTIC_ERROR',
                    'line': node.line,
                    'message': f"Function '{self.current_func['name']}' has return type void but returns {ret_type} at line {node.line}"
                })
            elif expected_type != 'void' and ret_type == 'void':
                self.errors.append({
                    'type': 'SEMANTIC_ERROR',
                    'line': node.line,
                    'message': f"Function '{self.current_func['name']}' expects return type {expected_type} but returns void at line {node.line}"
                })
            elif expected_type != 'void' and ret_type != 'void' and expected_type != 'unknown' and ret_type != 'unknown' and expected_type != ret_type:
                self.errors.append({
                    'type': 'SEMANTIC_ERROR',
                    'line': node.line,
                    'message': f"Return type mismatch: Function '{self.current_func['name']}' expects return type {expected_type} but returned {ret_type} at line {node.line}"
                })

    def _visit_PrintfStatement(self, node):
        self._generic_visit(node)

    def _visit_ScanfStatement(self, node):
        self._generic_visit(node)

    # ── Functions ─────────────────────────────────────────────────────────────
    def _visit_FunctionDecl(self, node):
        # children: Type, Identifier, ParamList, Block
        type_node = node.children[0] if len(node.children) > 0 else None
        id_node   = node.children[1] if len(node.children) > 1 else None
        param_node = node.children[2] if len(node.children) > 2 else None

        return_type = type_node.value if type_node else 'void'
        func_name = id_node.value if id_node else '?'
        line = node.line or 0

        # Count params & collect names/types
        param_count = len(param_node.children) if param_node else 0
        param_names = []
        if param_node:
            for p in param_node.children:
                p_type = p.children[0].value if len(p.children) > 0 else '?'
                p_name = p.children[1].value if len(p.children) > 1 else '?'
                param_names.append(f"{p_type} {p_name}")
        param_str = ', '.join(param_names)

        err = self.symbol_table.declare_function(func_name, return_type, param_count, line, param_names=param_str)
        if err:
            self.errors.append(err)

        # Set active function context for return checking
        self.current_func = {'name': func_name, 'return_type': return_type}

        # Enter scope for function body (params + local vars)
        self.symbol_table.enter_scope()

        # Declare parameters
        if param_node:
            for param in param_node.children:
                p_type = param.children[0].value if len(param.children) > 0 else 'unknown'
                p_name = param.children[1].value if len(param.children) > 1 else '?'
                p_line = param.line or line
                perr = self.symbol_table.declare(p_name, p_type, p_line)
                if perr:
                    self.errors.append(perr)

        # Visit the body block
        if len(node.children) > 3:
            self._visit(node.children[3])

        self.symbol_table.exit_scope()
        self.current_func = None

    def _visit_FunctionCall(self, node):
        func_name = node.value
        line = node.line or 0

        # Check if function is defined
        func = self.symbol_table.lookup_function(func_name)
        if func is None:
            # Don't error on built-in functions
            builtin = {'printf', 'scanf'}
            if func_name not in builtin:
                self.errors.append({
                    'type': 'SEMANTIC_ERROR',
                    'line': line,
                    'message': f"Call to undefined function '{func_name}' at line {line}"
                })
        else:
            # Check argument count
            arg_list = None
            for child in node.children:
                if child.node_type == 'ArgList':
                    arg_list = child
                    break
            arg_count = len(arg_list.children) if arg_list else 0
            if arg_count != func['param_count']:
                self.errors.append({
                    'type': 'SEMANTIC_ERROR',
                    'line': line,
                    'message': f"Function '{func_name}' expects {func['param_count']} argument(s) but got {arg_count}"
                })

        # Visit children (args only, skip the function name Identifier)
        for child in node.children:
            if child.node_type == 'ArgList':
                self._visit(child)
        
        return func['return_type'] if func else 'unknown'

    def _visit_ParamList(self, node):
        pass  # Handled by FunctionDecl

    def _visit_Param(self, node):
        pass  # Handled by FunctionDecl

    # ── Misc ──────────────────────────────────────────────────────────────────
    def _visit_ExpressionStatement(self, node):
        self._generic_visit(node)

    def _visit_GroupedExpr(self, node):
        return self._visit(node.children[0]) if node.children else None

    def _visit_ArgList(self, node):
        self._generic_visit(node)

    def _visit_Type(self, node):
        pass

    def _visit_Keyword(self, node):
        pass

    def _visit_AssignOp(self, node):
        pass

    def _visit_CompoundOp(self, node):
        pass