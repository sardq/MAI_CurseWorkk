import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np

MODEL_NAME = "huggingface/codeBERTa-small-v1"
class CodeEmbedder:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_safetensors=True)
        self.model = AutoModel.from_pretrained(MODEL_NAME, torch_dtype=torch.float32, use_safetensors=True)


        self.device = torch.device("cpu") 
        self.model.to(self.device)

    def get_embeddings(self, texts: list[str], batch_size: int = 16) -> np.ndarray:
        self.model.eval()
        embeddings = []
        
        total = len(texts)
        print(f"Processing {total} texts with batch_size={batch_size}...")

        with torch.no_grad():
            for i in range(0, total, batch_size):
                batch_texts = texts[i : i + batch_size]
                
                inputs = self.tokenizer(
                    batch_texts, 
                    return_tensors="pt", 
                    padding=True, 
                    truncation=True, 
                    max_length=128 
                ).to(self.device)
                
                outputs = self.model(**inputs)
                
                attention_mask = inputs['attention_mask']
                token_embeddings = outputs.last_hidden_state
                
                input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
                sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                mean_embedding = sum_embeddings / sum_mask
                
                embeddings.append(mean_embedding.cpu().numpy())
                
                del inputs, outputs, token_embeddings
        
        if embeddings:
            return np.vstack(embeddings)
        return np.array([])