from sentence_transformers import SentenceTransformer
import numpy as np
from functools import lru_cache
import hashlib

class EmbeddingService:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = SentenceTransformer("all-MiniLM-L6-v2")
        return cls._model

    @staticmethod
    def _hash_text(text: str) -> str:
        """
        Create a stable hash for caching embeddings.
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @classmethod
    @lru_cache(maxsize=5000)
    def _cached_encode(cls, text_hash: str, text: str) -> np.ndarray:
        """
        Cached single-text encoding.
        """
        model = cls.get_model()
        embedding = model.encode([text], show_progress_bar=False)
        return embedding[0]

    @classmethod
    def encode(cls, texts: list[str]) -> np.ndarray:
        """
        Encode texts with caching.
        Uses cache for single items, batch for new ones.
        """
        if not texts:
            return np.array([])

        embeddings = []

        for text in texts:
            clean_text = text.strip()
            if not clean_text:
                embeddings.append(None)
                continue

            text_hash = cls._hash_text(clean_text)
            emb = cls._cached_encode(text_hash, clean_text)
            embeddings.append(emb)

        return np.array(embeddings)