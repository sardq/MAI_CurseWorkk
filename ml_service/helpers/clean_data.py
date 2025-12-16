import os
import pandas as pd
import re
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

input_csv = os.path.join(BASE_DIR, "data", "code_bug_fix_pairs.csv")
output_csv = os.path.join(BASE_DIR, "data", "code_bug_fix_pairs_clean.csv") 

df = pd.read_csv(input_csv)

def remove_sample_id(code):
    return re.sub(r"# Sample ID.*", "", str(code)).strip()

df['buggy_code'] = df['buggy_code'].apply(remove_sample_id)
df['fixed_code'] = df['fixed_code'].apply(remove_sample_id)

df.to_csv(output_csv, index=False)

print(f"Обработка завершена. Результат сохранен в {output_csv}")
