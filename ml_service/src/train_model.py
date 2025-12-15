import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

DATA_PATH = "data/code_bug_fix_pairs.csv"
VECTORIZER_PATH = "src/vectorizer.pkl"
DB_PATH = "src/fix_database.pkl"

def train():
    df = pd.read_csv(DATA_PATH)
    df = df[["buggy_code", "fixed_code"]].dropna()

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        max_features=5000
    )

    X = vectorizer.fit_transform(df["buggy_code"])

    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(df, DB_PATH)

    print("ML model trained: vectorizer + fix database saved")

if __name__ == "__main__":
    train()
