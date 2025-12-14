import pycodestyle
import os
import tempfile
from typing import List, Dict

class CustomReport(pycodestyle.StandardReport):
    """Класс-перехватчик для сбора результатов анализа стиля в структуру данных."""
    def get_file_results(self) -> List[Dict]:
        self._deferred_print.sort()
        results = []
        for line_number, offset, code, text, doc in self._deferred_print:
            results.append({
                "line": line_number,
                "col": offset + 1,
                "code": code,
                "msg": text
            })
        return results

def check_style_maximal(code: str) -> List[Dict]:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        style_guide = pycodestyle.StyleGuide(
            reporter=CustomReport,
            ignore=[], 
            max_line_length=79 
        )
        report = style_guide.check_files([tmp_path])
        
        raw_errors = report.get_file_results()
        
        formatted_errors = []
        for err in raw_errors:
            formatted_errors.append({
                "msg": f"Нарушение стиля [{err['code']}]: {err['msg']}",
                "line": err['line'],
                "col": err['col'],
                "severity": "Warning" 
            })
            
        return formatted_errors
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)