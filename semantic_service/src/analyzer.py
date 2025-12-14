import ast
import re
from typing import List, Dict

class SemanticVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors = []
    def check_docstring(self, node):
        """Проверка наличия докстринга и его длины."""
        docstring = ast.get_docstring(node)
        
        if not docstring:
            self.errors.append({
                "line": node.lineno,
                "col": 0,
                "msg": f"Семантическая ошибка: Отсутствует документация (докстринг) для '{node.name}'.",
                "severity": "Warning",
                "suggestion": "Добавьте описание функции или класса."
            })
        elif len(docstring.split()) < 3:
            self.errors.append({
                "line": node.lineno,
                "col": 0,
                "msg": f"Семантическая ошибка: Слишком короткий докстринг для '{node.name}'.",
                "severity": "Info",
                "suggestion": "Описание должно быть содержательным."
            })

    def visit_FunctionDef(self, node):
        """Проверка функций."""
        self.check_docstring(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Проверка классов."""
        self.check_docstring(node)
        self.generic_visit(node)

def analyze_semantic(code: str) -> List[Dict]:
    """Основная функция семантического анализа."""
    errors = []
    
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return [] 
    
    visitor = SemanticVisitor()
    visitor.visit(tree)
    errors.extend(visitor.errors)
    
    
    comment_pattern = re.compile(r"#(.*)(TODO|FIXME|BUG)(.*)", re.IGNORECASE)
    
    for i, line in enumerate(code.splitlines()):
        match = comment_pattern.search(line)
        if match:
            errors.append({
                "line": i + 1,
                "col": match.start(2),
                "msg": f"Интеллектуальный анализ: Обнаружен маркер '{match.group(2)}' в комментарии.",
                "severity": "Info",
                "suggestion": "Удалите или исправьте отмеченный комментарий."
            })
            
    for err in errors:
        err['error_type'] = "Semantic"
    
    return errors