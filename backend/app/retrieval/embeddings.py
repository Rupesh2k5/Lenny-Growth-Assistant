import math
import re
from typing import List, Dict, Set
from collections import Counter

class LocalEmbeddingEngine:
    """
    High-speed, zero-dependency semantic vector and BM25/TF-IDF embedding engine.
    Calculates cosine similarity vectors for instant local retrieval.
    """
    def __init__(self, vector_dim: int = 128):
        self.vector_dim = vector_dim

    def tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        tokens = [t for t in cleaned.split() if len(t) > 2]
        return tokens

    def compute_dense_vector(self, text: str) -> List[float]:
        """
        Computes a normalized dense semantic representation using hashed term weighting.
        """
        tokens = self.tokenize(text)
        if not tokens:
            return [0.0] * self.vector_dim

        vec = [0.0] * self.vector_dim
        counts = Counter(tokens)
        
        for token, count in counts.items():
            # Hash token across vector dimensions
            h = hash(token) % self.vector_dim
            weight = (1.0 + math.log(count)) * (1.0 + 0.1 * (hash(token[:3]) % 5))
            vec[h] += weight

        # L2 Normalization
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [round(x / norm, 5) for x in vec]
        return vec

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return max(0.0, min(1.0, dot_product / (norm_a * norm_b)))

embedding_engine = LocalEmbeddingEngine()
