import ast

class LogicVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors = []
        self.variables = {}  

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables[target.id] = {'defined': node.lineno, 'used': False}
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id in self.variables:
            self.variables[node.id]['used'] = True
        self.generic_visit(node)

    def visit_If(self, node):
        if isinstance(node.test, ast.Constant):
            if node.test.value is True:
                self.errors.append({
                    "line": node.lineno,
                    "col": node.col_offset,
                    "msg": "Логическая ошибка: условие всегда True",
                    "severity": "Warning",
                    "suggestion": "Удалите проверку условия"
                })
            elif node.test.value is False:
                self.errors.append({
                    "line": node.lineno,
                    "col": node.col_offset,
                    "msg": "Логическая ошибка: недостижимый код (условие всегда False)",
                    "severity": "Critical",
                    "suggestion": "Удалите данный блок кода"
                })

        elif self.is_impossible_condition(node.test):
            self.errors.append({
                "line": node.lineno,
                "col": node.col_offset,
                "msg": "Логическая ошибка: условие всегда False",
                "severity": "Critical",
                "suggestion": "Проверьте условие"
            })

        self.generic_visit(node)

    def is_impossible_condition(self, node):
        """Простейший анализ для выражений с константами"""
        if isinstance(node, ast.Compare):
            if all(isinstance(c, ast.Constant) for c in [node.left] + node.comparators):
                left = node.left.value
                right = node.comparators[0].value
                op = node.ops[0]
                if isinstance(op, ast.Gt) and left <= right:
                    return True
                if isinstance(op, ast.Lt) and left >= right:
                    return True
                if isinstance(op, ast.GtE) and left < right:
                    return True
                if isinstance(op, ast.LtE) and left > right:
                    return True
                if isinstance(op, ast.Eq) and left != right:
                    return True
                if isinstance(op, ast.NotEq) and left == right:
                    return True

        if isinstance(node, ast.BoolOp) and all(isinstance(v, ast.Compare) for v in node.values):
            return all(self.is_impossible_condition(v) for v in node.values)

        return False

def analyze_logic(code: str) -> list:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    visitor = LogicVisitor()
    visitor.visit(tree)

    for var_name, info in visitor.variables.items():
        if not info['used'] and not var_name.startswith('_'):
            visitor.errors.append({
                "line": info['defined'],
                "col": 0,
                "msg": f"Неиспользуемая переменная: '{var_name}'",
                "severity": "Recommendation",
                "suggestion": f"Удалите переменную '{var_name}', если она не нужна."
            })

    return visitor.errors
