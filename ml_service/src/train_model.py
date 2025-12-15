import os
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_DIR, "..", "data", "code_bug_fix_pairs.csv")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")
DB_PATH = os.path.join(BASE_DIR, "fix_database.pkl")

def train():
    df = pd.read_csv(DATA_PATH)
    df = df[["buggy_code", "fixed_code", "commit_message"]].dropna()

    if df.empty:
            print("Dataset is empty, skipping training.")
            return
    
    vectorizer = TfidfVectorizer(
    analyzer="char_wb",  # "char_wb" учитывает границы слов (лучше для кода)
    ngram_range=(2, 4),  # Берем кусочки по 2-4 символа (больше шансов совпасть)
    min_df=1,            # Учитывать даже редкие ошибки
    max_features=5000
)

    X = vectorizer.fit_transform(df["buggy_code"])

    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(df, DB_PATH)

    print("ML model trained: vectorizer + fix database saved")

if __name__ == "__main__":
    train()
