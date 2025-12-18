import csv
import pandas as pd
import joblib
import os
from src.bert_utils import CodeEmbedder 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "code_bug_fix_pairs_merged.csv")
DB_VECTORS_PATH = os.path.join(BASE_DIR, "db_vectors.pkl")
DB_PATH = os.path.join(BASE_DIR, "fix_database.pkl")

def train():
    print(f"Loading data from: {DATA_PATH}")
    if not os.path.exists(DATA_PATH):
        print("CSV file not found.")
        return

    df = pd.read_csv(DATA_PATH, engine='python', quotechar = '"', quoting=csv.QUOTE_ALL, on_bad_lines='error', skipinitialspace=True)
    df = df.dropna(subset=["buggy_code"])
    
    df["train_text"] = df["buggy_code"].str.strip()

    if df.empty:
        print("Dataset is empty.")
        return

    embedder = CodeEmbedder()
    buggy_codes = df["buggy_code"].tolist()
    fixed_codes = df["fixed_code"].tolist()
    embedder.fine_tune(buggy_codes, fixed_codes, epochs=1, batch_size=8, lr=1e-5)
    
    vectors = embedder.get_embeddings(df["train_text"].tolist())

    joblib.dump(df, DB_PATH)
    joblib.dump(vectors, DB_VECTORS_PATH)


if __name__ == "__main__":
    train()