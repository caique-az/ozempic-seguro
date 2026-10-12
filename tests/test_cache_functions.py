"""
Testes para funções de cache globais.
"""

import pytest

from ozempic_seguro.core.cache import (
    _global_cache,
    invalidate_cache,
    get_cache_stats,
    cache_query,
    query_cache,
)


class TestGlobalCacheFunctions:
    """Testes para funções de cache globais"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        _global_cache.clear()
        yield
        _global_cache.clear()

    def test_invalidate_cache_all(self):
        """Testa invalidação de todo o cache"""
        _global_cache.set("key1", "value1")
        _global_cache.set("key2", "value2")

        count = invalidate_cache()

        assert count >= 0
        assert _global_cache.get("key1") is None

    def test_invalidate_cache_pattern(self):
        """Testa invalidação por padrão"""
        _global_cache.set("user:1", "data1")
        _global_cache.set("user:2", "data2")
        _global_cache.set("other:1", "data3")

        count = invalidate_cache("user")

        assert count >= 0

    def test_get_cache_stats(self):
        """Testa obtenção de estatísticas"""
        _global_cache.set("key1", "value1")
        _global_cache.get("key1")  # hit
        _global_cache.get("nonexistent")  # miss

        stats = get_cache_stats()

        assert isinstance(stats, dict)
        assert "size" in stats
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats

    def test_cache_query_generates_key(self):
        """Testa geração de chave para query"""
        key = cache_query("SELECT * FROM users WHERE id = ?", (1,))

        assert isinstance(key, str)
        assert len(key) > 0

    def test_cache_query_same_query_same_key(self):
        """Testa que mesma query gera mesma chave"""
        key1 = cache_query("SELECT * FROM users", ())
        key2 = cache_query("SELECT * FROM users", ())

        assert key1 == key2

    def test_cache_query_different_params_different_key(self):
        """Testa que parâmetros diferentes geram chaves diferentes"""
        key1 = cache_query("SELECT * FROM users WHERE id = ?", (1,))
        key2 = cache_query("SELECT * FROM users WHERE id = ?", (2,))

        assert key1 != key2


class TestQueryCache:
    """Testes para query_cache"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        query_cache.clear()
        yield
        query_cache.clear()

    def test_query_cache_set_get(self):
        """Testa set e get no query_cache"""
        query_cache.set("query1", {"result": "data"})

        result = query_cache.get("query1")

        assert result == {"result": "data"}

    def test_query_cache_clear(self):
        """Testa clear do query_cache"""
        query_cache.set("query1", "data1")
        query_cache.set("query2", "data2")

        query_cache.clear()

        assert query_cache.get("query1") is None
        assert query_cache.get("query2") is None
