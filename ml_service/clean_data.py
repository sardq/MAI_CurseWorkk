import pandas as pd
import re

DATA_PATH = "data/code_bug_fix_pairs.csv"

def clean_code(code):
    if not isinstance(code, str):
        return ""
    
    # 1. Удаляем комментарии вида # Sample ID: ...
    code = re.sub(r'# Sample ID:.*', '', code)
    
    code = re.sub(r'#.*', '', code)
    
    # 3. Заменяем переносы строк на пробелы (чтобы векторайзер не спотыкался)
    code = code.replace('\n', ' ')
    
    # 4. Удаляем лишние пробелы (два и более подряд)
    code = re.sub(r'\s+', ' ', code).strip()
    
    return code

def clean_dataset():
    print(f"Читаем {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    print("Очистка данных...")
    # Применяем очистку к колонкам с кодом
    df["buggy_code"] = df["buggy_code"].apply(clean_code)
    df["fixed_code"] = df["fixed_code"].apply(clean_code)
    
    # Удаляем дубликаты, которые могли появиться после очистки
    initial_len = len(df)
    df = df.drop_duplicates(subset=["buggy_code"])
    print(f"Удалено дубликатов: {initial_len - len(df)}")
    
    # Удаляем пустые строки
    df = df[df["buggy_code"].str.len() > 3] # Убираем совсем мусор
    
    df.to_csv(DATA_PATH, index=False)
    print("✅ Датасет очищен и сохранен! Теперь запустите обучение.")

if __name__ == "__main__":
    clean_dataset()