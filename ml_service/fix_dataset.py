import pandas as pd
import os
from src.train_model import train  # Импортируем вашу функцию обучения

# Путь к датасету
CSV_PATH = "data/code_bug_fix_pairs.csv"

# Данные, которые мы хотим добавить (именно то, что приходит от анализатора)
# buggy_code = Текст ошибки, который присылает Report Service
# fixed_code = Заглушка (не важна для ML поиска, важна для структуры)
# commit_message = Рекомендация, которую мы хотим отдать пользователю
new_data = [
    {
        "buggy_code": "invalid syntax",
        "fixed_code": "Syntax Corrected",
        "commit_message": "Проверьте синтаксис: возможно, пропущено двоеточие, скобка или кавычка."
    },
    {
        "buggy_code": "expected ':'",
        "fixed_code": ":",
        "commit_message": "Пропущено двоеточие в конце оператора (if, def, while, for)."
    },
    {
        "buggy_code": "unexpected indent",
        "fixed_code": "pass",
        "commit_message": "Ошибка отступа. Убедитесь, что отступы выровнены (обычно 4 пробела)."
    },
    {
        "buggy_code": "unindent does not match any outer indentation level",
        "fixed_code": "pass",
        "commit_message": "Ошибка отступа. Смешаны табы и пробелы или неверный уровень вложенности."
    },
    {
        "buggy_code": "def foo()",  # Ваш пример с низкой уверенностью
        "fixed_code": "def foo():",
        "commit_message": "В определении функции пропущено двоеточие."
    }
]

def boost_dataset():
    print(f"Загрузка {CSV_PATH}...")
    try:
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["buggy_code", "fixed_code", "commit_message"])

    # Создаем DataFrame из новых данных
    new_df = pd.DataFrame(new_data)

    # Проверяем, нет ли уже таких записей, чтобы не дублировать
    # (простая проверка по первому столбцу)
    filtered_new_df = new_df[~new_df["buggy_code"].isin(df["buggy_code"])]

    if not filtered_new_df.empty:
        # Объединяем старый и новый датасеты
        final_df = pd.concat([df, filtered_new_df], ignore_index=True)
        
        # Сохраняем обратно в CSV
        final_df.to_csv(CSV_PATH, index=False)
        print(f"✅ Добавлено {len(filtered_new_df)} новых записей для обучения.")
    else:
        print("⚠️ Эти записи уже есть в датасете.")

    print("🚀 Запускаем переобучение модели...")
    train()
    print("🏁 Готово! Теперь проверьте уверенность в Jupyter Notebook.")

if __name__ == "__main__":
    boost_dataset()