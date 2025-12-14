import ast

class LogicVisitor(ast.NodeVisitor):
    def init(self):
        self.errors = []
        self.variables = {}  

    def visit_Assign(self, node):
        """Отслеживание присваивания переменных"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables[target.id] = {'defined': node.lineno, 'used': False}
        self.generic_visit(node)

    def visit_Name(self, node):
        """Отслеживание использования переменных"""
        if isinstance(node.ctx, ast.Load) and node.id in self.variables:
            self.variables[node.id]['used'] = True
        self.generic_visit(node)

    def visit_If(self, node):
        """Поиск логических ошибок: if True / if False """
        if isinstance(node.test, ast.Constant):
            if node.test.value is True:
                self.errors.append({
                    "line": node.lineno,
                    "col": node.col_offset,
                    "msg": "Логическая ошибка: Условие 'if True' всегда выполняется.",
                    "severity": "Warning",
                    "suggestion": "Удалите проверку условия."
                })
            elif node.test.value is False:
                self.errors.append({
                    "line": node.lineno,
                    "col": node.col_offset,
                    "msg": "Логическая ошибка: Недостижимый код (if False).",
                    "severity": "Critical",
                    "suggestion": "Удалите данный блок кода."
                })
        self.generic_visit(node)

def analyze_logic(code: str) -> list:
    """Функция запуска анализа"""
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