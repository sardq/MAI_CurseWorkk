import asyncio
from src.database import AsyncSessionLocal
from src.models import KnowledgeDB 

async def seed_knowledge_base():
    async with AsyncSessionLocal() as db:
        
        entries = [
            KnowledgeDB(
                error_type="Syntax",
                keyword_pattern=":", 
                description="В Python двоеточие обязательно в конце условий (if), циклов (for/while) и объявлений функций (def).",
                correction="Добавьте двоеточие ':' в конце строки.",
                severity_level="Critical"
            ),
            KnowledgeDB(
                error_type="Syntax",
                keyword_pattern="indent", 
                description="Python использует отступы для выделения блоков кода. Смешивание пробелов и табуляции или неверное количество пробелов вызывает ошибку.",
                correction="Выровняйте отступы. Рекомендуется использовать 4 пробела.",
                severity_level="Critical"
            ),
            KnowledgeDB(
                error_type="Syntax",
                keyword_pattern="parenthesis",
                description="Непарные скобки.",
                correction="Проверьте, закрыты ли все скобки (, [, {.",
                severity_level="Critical"
            ),
            KnowledgeDB(
                error_type="Syntax",
                keyword_pattern="", 
                description="Общая синтаксическая ошибка.",
                correction="Проверьте корректность конструкции языка Python.",
                severity_level="Critical"
            ),

            KnowledgeDB(
                error_type="Logic", 
                keyword_pattern="условие всегда True",
                description="Условие if всегда истинно, код внутри будет выполняться всегда, проверка бессмысленна.",
                correction="Удалите проверку или исправьте условие.",
                severity_level="Warning"
            ),
            
             KnowledgeDB(
                error_type="Style",
                keyword_pattern="line too long",
                description="Строка превышает рекомендованную длину (обычно 79 символов).",
                correction="Разбейте строку на несколько частей.",
                severity_level="Info"
            ),
        ]

        for entry in entries:
            db.add(entry)
        
        await db.commit()
        print("База знаний успешно обновлена!")

if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())