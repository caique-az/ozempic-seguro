"""
Sistema de cache em memória para otimização de performance.
Implementa cache LRU (Least Recently Used) com TTL (Time To Live).
"""

import hashlib
import threading
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any


class CacheEntry:
    """Representa uma entrada no cache com TTL"""

    def __init__(self, value: Any, ttl_seconds: int = 300):
        self.value = value
        self.created_at = datetime.now()
        self.ttl_seconds = ttl_seconds
        self.access_count = 0

    def is_expired(self) -> bool:
        """Verifica se a entrada expirou"""
        if self.ttl_seconds <= 0:
            return False  # TTL infinito

        age = datetime.now() - self.created_at
        return age.total_seconds() > self.ttl_seconds

    def access(self) -> Any:
        """Registra acesso e retorna valor"""
        self.access_count += 1
        return self.value


class MemoryCache:
    """
    Cache em memória thread-safe com suporte a TTL e LRU.
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Inicializa o cache.

        Args:
            max_size: Tamanho máximo do cache
            default_ttl: TTL padrão em segundos (5 minutos)
        """
        self._cache: dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        """
        Obtém valor do cache.

        Args:
            key: Chave do cache

        Returns:
            Valor se existir e não expirado, None caso contrário
        """
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]

                if entry.is_expired():
                    # Remove entrada expirada
                    del self._cache[key]
                    self._misses += 1
                    return None

                self._hits += 1
                return entry.access()

            self._misses += 1
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Define valor no cache.

        Args:
            key: Chave do cache
            value: Valor a armazenar
            ttl: TTL específico em segundos (opcional)
        """
        with self._lock:
            # Verifica limite de tamanho
            if len(self._cache) >= self._max_size:
                self._evict_lru()

            ttl = ttl if ttl is not None else self._default_ttl
            self._cache[key] = CacheEntry(value, ttl)

    def delete(self, key: str) -> bool:
        """
        Remove entrada do cache.

        Args:
            key: Chave a remover

        Returns:
            True se removido, False se não existia
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Limpa todo o cache"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def _evict_lru(self) -> None:
        """Remove entrada menos recentemente usada"""
        if not self._cache:
            return

        # Encontra entrada com menor access_count ou mais antiga
        lru_key = min(
            self._cache.keys(),
            key=lambda k: (self._cache[k].access_count, self._cache[k].created_at),
        )

        del self._cache[lru_key]

    def get_stats(self) -> dict[str, Any]:
        """Retorna estatísticas do cache"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.2f}%",
                "total_requests": total_requests,
            }

    def cleanup_expired(self) -> int:
        """
        Remove todas as entradas expiradas.

        Returns:
            Número de entradas removidas
        """
        with self._lock:
            expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]

            for key in expired_keys:
                del self._cache[key]

            return len(expired_keys)


# Cache global compartilhado
_global_cache = MemoryCache()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator para cachear resultados de funções.

    Args:
        ttl: Time to live em segundos
        key_prefix: Prefixo para a chave do cache

    Exemplo:
        @cached(ttl=600, key_prefix="user")
        def get_user(user_id: int):
            return database.fetch_user(user_id)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gera chave única baseada na função e argumentos
            cache_key = _generate_cache_key(func, args, kwargs, key_prefix)

            # Tenta obter do cache
            cached_value = _global_cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Executa função e armazena resultado
            result = func(*args, **kwargs)
            _global_cache.set(cache_key, result, ttl)

            return result

        # Adiciona método para limpar cache desta função
        wrapper.clear_cache = lambda: _clear_function_cache(func, key_prefix)

        return wrapper

    return decorator


def _generate_cache_key(func: Callable, args: tuple, kwargs: dict, prefix: str) -> str:
    """Gera chave única para o cache baseada na função e argumentos"""
    key_parts = [prefix, func.__module__, func.__name__, str(args), str(sorted(kwargs.items()))]

    key_string = ":".join(filter(None, key_parts))

    # Hash para evitar chaves muito longas
    key_hash = hashlib.md5(key_string.encode()).hexdigest()

    return f"{prefix}:{func.__name__}:{key_hash}" if prefix else f"{func.__name__}:{key_hash}"


def _clear_function_cache(func: Callable, prefix: str) -> None:
    """Limpa cache de uma função específica"""
    pattern = f"{prefix}:{func.__name__}" if prefix else func.__name__

    keys_to_delete = [key for key in _global_cache._cache if key.startswith(pattern)]

    for key in keys_to_delete:
        _global_cache.delete(key)


def invalidate_cache(pattern: str | None = None) -> int:
    """
    Invalida entradas do cache que correspondem ao padrão.

    Args:
        pattern: Padrão para match de chaves (None limpa tudo)

    Returns:
        Número de entradas invalidadas
    """
    if pattern is None:
        size = len(_global_cache._cache)
        _global_cache.clear()
        return size

    count = 0
    keys_to_delete = [key for key in _global_cache._cache if pattern in key]

    for key in keys_to_delete:
        if _global_cache.delete(key):
            count += 1

    return count


def get_cache_stats() -> dict[str, Any]:
    """Obtém estatísticas do cache global"""
    return _global_cache.get_stats()


# Cache específico para queries de banco
query_cache = MemoryCache(max_size=500, default_ttl=60)


def cache_query(query: str, params: tuple = (), ttl: int = 60) -> str:
    """
    Gera chave de cache para uma query SQL.

    Args:
        query: Query SQL
        params: Parâmetros da query
        ttl: TTL em segundos

    Returns:
        Chave de cache gerada
    """
    key_data = f"{query}:{params}"
    return hashlib.md5(key_data.encode()).hexdigest()
