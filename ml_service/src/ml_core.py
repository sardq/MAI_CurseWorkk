import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
from src.bert_utils import CodeEmbedder

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_VECTORS_PATH = os.path.join(BASE_DIR, "db_vectors.pkl")
DB_PATH = os.path.join(BASE_DIR, "fix_database.pkl")

CONFIDENCE_THRESHOLD = 0.75

class MLAnalyzer:
    def __init__(self):
        self.embedder = None
        self.db = None
        self.db_vectors = None
        self.load_model()

    def load_model(self):
        if os.path.exists(DB_VECTORS_PATH) and os.path.exists(DB_PATH):
            self.db = joblib.load(DB_PATH)
            self.db_vectors = joblib.load(DB_VECTORS_PATH)

        try:
            self.embedder = CodeEmbedder()
        except Exception as e:
            print(f" Failed to load CodeBERT: {e}")

    def reload_model(self):
        if os.path.exists(DB_VECTORS_PATH) and os.path.exists(DB_PATH):
            self.db = joblib.load(DB_PATH)
            self.db_vectors = joblib.load(DB_VECTORS_PATH)

    def predict(self, code_fragment: str, context: str | None = None) -> dict:
        if self.embedder is None or self.db_vectors is None:
            return {"confidence": 0.0, "ml_correction": "Model not ready"}

        if not code_fragment:
             return {"confidence": 0.0, "ml_correction": ""}

        query_vec = self.embedder.get_embeddings([code_fragment]) 

        similarities = cosine_similarity(query_vec, self.db_vectors).flatten()
        best_idx = int(np.argmax(similarities))
        confidence = float(similarities[best_idx])
        
        row = self.db.iloc[best_idx]

        severity = "Info"
        if confidence >= 0.85: severity = "Critical"
        elif confidence >= 0.70: severity = "Warning"

        if confidence < CONFIDENCE_THRESHOLD:
             return {
                "ml_error_type": "ML_UNCERTAIN",
                "ml_severity": "Info",
                "ml_correction": "",
                "confidence": confidence,
            }

        return {
            "ml_error_type": "ML_Contextual_Fix", 
            "ml_severity": severity,
            "ml_correction": row["commit_message"],
            "confidence": confidence,
        }

ml_analyzer = MLAnalyzer()