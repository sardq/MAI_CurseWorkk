import ast
from collections import Counter


class ASTSummaryVisitor(ast.NodeVisitor):
    def __init__(self):
        self.node_counter = Counter()

    def generic_visit(self, node):
        self.node_counter[type(node).__name__] += 1
        super().generic_visit(node)


def analyze_syntax_with_ast(code: str):
    errors = []
    ast_summary = {
        "total_nodes": 0,
        "node_types": {},
        "functions": 0,
        "classes": 0,
        "loops": 0,
        "conditions": 0
    }

    try:
        tree = ast.parse(code)

        visitor = ASTSummaryVisitor()
        visitor.visit(tree)

        ast_summary["node_types"] = dict(visitor.node_counter)
        ast_summary["total_nodes"] = sum(visitor.node_counter.values())
        ast_summary["functions"] = visitor.node_counter.get("FunctionDef", 0)
        ast_summary["classes"] = visitor.node_counter.get("ClassDef", 0)
        ast_summary["loops"] = (
            visitor.node_counter.get("For", 0)
            + visitor.node_counter.get("While", 0)
        )
        ast_summary["conditions"] = visitor.node_counter.get("If", 0)

    except SyntaxError as e:
        errors.append({
            "error_type": "Syntax",
            "message": e.msg,
            "line": e.lineno or 1,
            "column": e.offset or 1,
            "severity": "Critical",
            "suggestion": "Проверьте корректность синтаксиса Python-кода"
        })

    return errors, ast_summary
