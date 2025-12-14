import joblib
import os
import numpy as np
import random
from typing import Dict, List
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# --- Параметры модели ---
MAX_WORDS = 10000      # Максимальное количество слов (токенов) в словаре
MAX_LEN = 50           # Максимальная длина последовательности (фрагмента кода)
EMBEDDING_DIM = 16     # Размерность векторного представления

# --- Имитация реальных данных для обучения ---
def generate_code_data() -> (List[str], List[str]):
    """Генерирует примеры кода и соответствующие метки ошибок."""
    style_samples = [
        "if a==b:print(c)", "def func( x , y):", "result =  1 + 2", 
        "long_variable_name_one = 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10"
    ]
    logic_samples = [
        "if True == False:", "while (x > 10) and (x < 5):", "return x / 0",
        "if 'a' in [1, 2, 3]:"
    ]
    security_samples = [
        "import os; os.system(cmd)", "user_input = input(); eval(user_input)",
        "db.execute(f'SELECT * FROM users WHERE name={user}')"
    ]

    X_train = style_samples + logic_samples + security_samples
    # Метки: 0 - Style, 1 - Logic, 2 - Security
    y_labels = [0] * len(style_samples) + [1] * len(logic_samples) + [2] * len(security_samples)
    
    return X_train, np.array(y_labels)

def train_and_save_model():
    """Обучает простую одномерную свёрточную нейронную сеть (Conv1D)."""
    
    X_train, y_train = generate_code_data()
    
    tokenizer = Tokenizer(num_words=MAX_WORDS, char_level=True, split='')
    tokenizer.fit_on_texts(X_train)
    
    sequences = tokenizer.texts_to_sequences(X_train)
    X_padded = pad_sequences(sequences, maxlen=MAX_LEN)
    
    model = Sequential([
        Embedding(len(tokenizer.word_index) + 1, EMBEDDING_DIM, input_length=MAX_LEN),
        Conv1D(filters=32, kernel_size=3, activation='relu'),
        GlobalMaxPooling1D(),
        Dense(3, activation='softmax') 
    ])
    
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    
    model.fit(X_padded, y_train, epochs=10, verbose=0)

    model.save('src/trained_model.h5')
    joblib.dump(tokenizer, 'src/tokenizer.pkl')
    print("Realistic ML model (Keras) trained and saved.")


class MLAnalyzer:
    def init(self):
        self.model = None
        self.tokenizer = None
        self.LABEL_MAP = {0: "Style", 1: "Logic", 2: "Security"}
        
        if not os.path.exists('src/trained_model.h5'):
            train_and_save_model() 
            
        try:
            self.model = load_model('src/trained_model.h5')
            self.tokenizer = joblib.load('src/tokenizer.pkl')
        except Exception as e:
            print(f"Ошибка загрузки ML-модели: {e}")
            raise RuntimeError("ML model failed to load.")

    def predict(self, code_fragment: str, context: Optional[str] = None) -> Dict:
        """Предсказывает тип ошибки и генерирует рекомендацию."""
        
        sequences = self.tokenizer.texts_to_sequences([code_fragment])
        X_test = pad_sequences(sequences, maxlen=MAX_LEN)
        
        predictions = self.model.predict(X_test)[0]
        predicted_class_index = np.argmax(predictions)
        confidence = predictions[predicted_class_index]
        
        predicted_label = self.LABEL_MAP.get(predicted_class_index, "Unknown")
        
        if predicted_label == "Logic":
            correction = "Модель предсказала логическую ошибку. Проверьте условия выхода из циклов."
            severity = "Critical"
            ml_type = "ML: Logical Ambiguity"
        elif predicted_label == "Style":
            correction = "Модель предсказала стилевую проблему. Улучшите форматирование (PEP 8)."
            severity = "Info"
            ml_type = "ML: Style Deviation"
        elif predicted_label == "Security":
            correction = "Модель обнаружила потенциальную уязвимость (SQL Injection/RCE). НЕМЕДЛЕННО ИСПРАВЬТЕ!"
            severity = "Critical"
            ml_type = "ML: Vulnerability"
        else:
            correction = "Модель не смогла классифицировать фрагмент кода."
            severity = "Unknown"
            ml_type = "ML: Unclassified"
            
        return {
            "ml_error_type": ml_type,
            "ml_severity": severity,
            "ml_correction": correction,
            "confidence": float(confidence)
        }

ml_analyzer = MLAnalyzer()