import hashlib
import os
import pickle
import json
from typing import Optional, Any, List

class EmbeddingCache:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, content: Any, model: str) -> str:
        """Generate cache key from text and model"""
        if isinstance(content, list):
            # Para listas, criar uma chave única baseada no conteúdo
            content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        else:
            content_str = str(content)
        
        key_content = f"{content_str}:{model}"
        return hashlib.md5(key_content.encode('utf-8')).hexdigest()

    def _get_batch_cache_key(self, texts: List[str], model: str) -> str:
        """Generate cache key for batch of texts"""
        return self._get_cache_key(texts, f"batch_{model}")
    
    def get_batch(self, texts: List[str], model: str) -> Optional[List[Any]]:
        """Get cached embeddings for batch of texts"""
        batch_key = self._get_batch_cache_key(texts, model)
        cache_file = os.path.join(self.cache_dir, f"{batch_key}.pkl")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None

    def set_batch(self, texts: List[str], model: str, embeddings: List[Any]) -> None:
        """Cache embeddings for batch of texts"""
        if len(texts) != len(embeddings):
            raise ValueError("Numero de textos deve ser igual ao numero de embeddings")
        
        batch_key = self._get_batch_cache_key(texts, model)
        cache_file = os.path.join(self.cache_dir, f"{batch_key}.pkl")
        
        with open(cache_file, 'wb') as f:
            pickle.dump(embeddings, f)
        
        # Também cache individualmente para hits parciais futuros
        for text, embedding in zip(texts, embeddings):
            self.set(text, model, embedding)
    
    def get(self, text: str, model: str) -> Optional[Any]:
        """Get cached embedding"""
        key = self._get_cache_key(text, model)
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def set(self, text: str, model: str, embedding: Any) -> None:
        """Cache embedding"""
        key = self._get_cache_key(text, model)
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        
        with open(cache_file, 'wb') as f:
            pickle.dump(embedding, f)