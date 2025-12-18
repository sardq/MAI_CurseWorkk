import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from torch.utils.data import Dataset, DataLoader 
import torch.nn as nn

MODEL_NAME = "huggingface/codeBERTa-small-v1"

class BugFixDataset(Dataset):
    def __init__(self, buggy_codes, fixed_codes):
        self.buggy_codes = buggy_codes
        self.fixed_codes = fixed_codes

    def __len__(self):
        return len(self.buggy_codes)

    def __getitem__(self, idx):
        return {
            "buggy": self.buggy_codes[idx],
            "fixed": self.fixed_codes[idx]
        }


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
    def fine_tune(self, buggy_codes, fixed_codes, epochs=1, batch_size=8, lr=1e-5):
        self.model.train()
        dataset = BugFixDataset(buggy_codes, fixed_codes)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr)
        loss_fn = nn.CosineEmbeddingLoss(margin=0.5)  

        for epoch in range(epochs):
            total_loss = 0.0
            for batch in loader:
                optimizer.zero_grad()

                buggy_inputs = self.tokenizer(
                    batch["buggy"], return_tensors="pt", padding=True, truncation=True, max_length=128
                ).to(self.device)
                buggy_out = self.model(**buggy_inputs).last_hidden_state
                buggy_mask = buggy_inputs['attention_mask'].unsqueeze(-1).expand(buggy_out.size()).float()
                buggy_vec = (buggy_out * buggy_mask).sum(1) / torch.clamp(buggy_mask.sum(1), min=1e-9)

                fixed_inputs = self.tokenizer(
                    batch["fixed"], return_tensors="pt", padding=True, truncation=True, max_length=128
                ).to(self.device)
                fixed_out = self.model(**fixed_inputs).last_hidden_state
                fixed_mask = fixed_inputs['attention_mask'].unsqueeze(-1).expand(fixed_out.size()).float()
                fixed_vec = (fixed_out * fixed_mask).sum(1) / torch.clamp(fixed_mask.sum(1), min=1e-9)

                labels = torch.ones(buggy_vec.size(0)).to(self.device)
                loss = loss_fn(buggy_vec, fixed_vec, labels)

                loss.backward()
                optimizer.step()

                total_loss += loss.item()
            print(f"Epoch {epoch+1}/{epochs} — Loss: {total_loss/len(loader):.4f}")

        self.model.eval()
        print("Fine-tuning завершен. Теперь можно пересчитать embeddings для базы.")