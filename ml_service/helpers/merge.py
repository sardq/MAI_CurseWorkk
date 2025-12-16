import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_1 = os.path.join(BASE_DIR, "data", "code_bug_fix_pairs_final.csv")
FILE_2 = os.path.join(BASE_DIR, "data", "code_bug_fix_pairs.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "code_bug_fix_pairs_merged.csv")



def merge_and_deduplicate():
    dfs = []
    for fpath in [FILE_1, FILE_2]:
        if os.path.exists(fpath):
            dfs.append(pd.read_csv(fpath))
    if not dfs:
        return

    merged_df = pd.concat(dfs, ignore_index=True)
    total_before = len(merged_df)


    merged_df["buggy_code_clean"] = merged_df["buggy_code"].str.replace(r"# Sample ID: \d+", "", regex=True).str.strip()

    merged_df = merged_df.dropna(subset=["buggy_code_clean", "fixed_code"])
    merged_df = merged_df.drop_duplicates(subset=["buggy_code_clean", "fixed_code"], keep="first")

    merged_df["id"] = range(1, len(merged_df)+1)
    merged_df["commit_url"] = merged_df.get("commit_url", "https://github.com/example/merged").fillna("https://github.com/example/merged")
    merged_df["date"] = merged_df.get("date", "2025-01-01").fillna("2025-01-01")

    merged_df.to_csv(OUTPUT_FILE, index=False)

if __name__ == "__main__":
    merge_and_deduplicate()
