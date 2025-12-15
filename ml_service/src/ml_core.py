import re
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

# Пути к файлам модели
# Используем os.path, чтобы пути работали корректно независимо от точки запуска
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")
DB_PATH = os.path.join(BASE_DIR, "fix_database.pkl")

class MLAnalyzer:
    def __init__(self):
        self.vectorizer = None
        self.db = None
        self.db_vectors = None
        self.load_model()

    def load_model(self):
        """Загружает модель и базу данных в память."""
        if os.path.exists(VECTORIZER_PATH) and os.path.exists(DB_PATH):
            self.vectorizer = joblib.load(VECTORIZER_PATH)
            self.db = joblib.load(DB_PATH)
            # Векторизуем базу сразу при загрузке, чтобы не делать это каждый раз при запросе
            self.db_vectors = self.vectorizer.transform(self.db["buggy_code"])
            print("✅ ML Model loaded into memory.")
        else:
            print("⚠️ Model files not found. Please run train_model.py first.")

    def reload_model(self):
        """Перезагружает модель (используется после дообучения)."""
        print("Reloading model...")
        self.load_model()

    def preprocess_query(self, code: str) -> str:
        """Очищает запрос пользователя от мусора, чтобы повысить точность."""
        if not code:
            return ""
        # Заменяем переносы строк на пробелы
        code = code.replace('\n', ' ')
        # Удаляем лишние пробелы (два и более подряд)
        code = re.sub(r'\s+', ' ', code).strip()
        return code

    def predict(self, code_fragment: str, context: str = None) -> dict:
        """
        Основной метод: принимает код, находит похожий баг и возвращает решение.
        """
        if self.vectorizer is None or self.db is None:
            return {
                "ml_error_type": "ML_Error",
                "ml_severity": "Info",
                "ml_correction": "Model not loaded",
                "confidence": 0.0
            }

        # 1. Очищаем запрос (важный шаг для повышения уверенности!)
        clean_code = self.preprocess_query(code_fragment)
        
        # 2. Векторизуем запрос
        try:
            query_vec = self.vectorizer.transform([clean_code])
        except ValueError:
            # Если запрос пустой или содержит недопустимые символы
            return {
                "ml_error_type": "ML_Unknown",
                "ml_severity": "Info",
                "ml_correction": "",
                "confidence": 0.0
            }

        # 3. Считаем сходство (Cosine Similarity)
        similarities = cosine_similarity(query_vec, self.db_vectors).flatten()
        
        # 4. Находим лучший результат
        best_idx = np.argmax(similarities)
        confidence = float(similarities[best_idx])
        
        # Получаем строку из базы данных (DataFrame)
        row = self.db.iloc[best_idx]

        # 5. Возвращаем результат
        return {
            "ml_error_type": "ML_Suggestion", # Можно брать из контекста или базы
            "ml_severity": "Warning" if confidence > 0.8 else "Info",
            "ml_correction": row["commit_message"],
            "confidence": confidence
        }

# Создаем экземпляр анализатора
ml_analyzer = MLAnalyzer()