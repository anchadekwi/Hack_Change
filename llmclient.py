import requests
import json
import numpy as np


class OpenRouterEmbedderClient:
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"

    def embed(self, text: str) -> np.ndarray:
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost",
            "X-Title": "Embedding App",
        }

        payload = {"model": self.model_name, "input": text}

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()

        if "data" in data and len(data["data"]) > 0:
            embedding = data["data"][0]["embedding"]
            return np.array(embedding)
        else:
            raise ValueError("Не удалось получить эмбеддинг из ответа")

    def embed_batch(self, texts: list) -> list:
        embeddings = []
        for text in texts:
            embedding = self.embed(text)
            if embedding.size > 0:
                embeddings.append(embedding)
        return embeddings


def main():
    API_KEY = (
        "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"
    )

    embedder = OpenRouterEmbedderClient("text-embedding-ada-002", API_KEY)

    text = "сколько гусей у бабули в русской сказке жили у бабуси"
    embedding = embedder.embed(text)

    min1 = f"{np.min(embedding):.4f}"
    max2 = f"{np.max(embedding):.4f}"


# Дополнительный класс с расширенными функциями
class AdvancedEmbedder(OpenRouterEmbedderClient):
    def __init__(self, model_name: str, api_key: str):
        super().__init__(model_name, api_key)

    def cosine_similarity(self, text1: str, text2: str) -> float:

        emb1 = self.embed(text1)
        emb2 = self.embed(text2)

        if emb1.size == 0 or emb2.size == 0:
            return 0.01
        emb1_norm = emb1 / np.linalg.norm(emb1)
        emb2_norm = emb2 / np.linalg.norm(emb2)

        similarity = np.dot(emb1_norm, emb2_norm)
        return float(similarity)

    def find_most_similar(self, query: str, texts: list) -> dict:
        query_embedding = self.embed(query)
        if query_embedding.size == 0:
            return {"index": -1, "similarity": 0.0, "text": ""}

        similarities = []
        for text in texts:
            text_embedding = self.embed(text)
            if text_embedding.size > 0:
                query_norm = query_embedding / np.linalg.norm(query_embedding)
                text_norm = text_embedding / np.linalg.norm(text_embedding)
                similarity = np.dot(query_norm, text_norm)
                similarities.append(similarity)
            else:
                similarities.append(0.0)

        max_index = np.argmax(similarities)
        return {
            "index": max_index,
            "similarity": float(similarities[max_index]),
            "text": texts[max_index],
        }


# # Тестирование расширенного функционала
# def test_advanced_features():
#     API_KEY = (
#         "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"
#     )
#     advanced_embedder = AdvancedEmbedder("text-embedding-ada-002", API_KEY)

#     # Тестовые тексты
#     texts = [
#         "гуси летят на юг",
#         "бабушка печет пироги",
#         "сказка про гусей и бабушку",
#         "компьютерные технологии",
#         "программирование на Python",
#     ]

#     query = "гуси у бабуси в сказке"

#     print("🔍 Поиск наиболее похожего текста...")
#     result = advanced_embedder.find_most_similar(query, texts)

#     print(f"✅ Наиболее похожий текст:")
#     print(f"   📝 Текст: {result['text']}")
#     print(f"   🎯 Схожесть: {result['similarity']:.4f}")
#     print(f"   📍 Индекс: {result['index']}")


# test_advanced_features()
