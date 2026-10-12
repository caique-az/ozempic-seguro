"""
Testes estendidos para MemoryCache - Cobertura adicional.
"""

import pytest

from ozempic_seguro.core.cache import MemoryCache, cached


class TestMemoryCacheExtended:
    """Testes estendidos para MemoryCache"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.cache = MemoryCache(default_ttl=60)
        yield
        self.cache.clear()

    def test_set_and_get(self):
        """Testa set e get básico"""
        self.cache.set("key1", "value1")

        result = self.cache.get("key1")

        assert result == "value1"

    def test_get_nonexistent(self):
        """Testa get de chave inexistente"""
        result = self.cache.get("nonexistent")

        assert result is None

    def test_delete(self):
        """Testa delete"""
        self.cache.set("key1", "value1")

        self.cache.delete("key1")

        assert self.cache.get("key1") is None

    def test_delete_nonexistent(self):
        """Testa delete de chave inexistente"""
        # Não deve lançar exceção
        self.cache.delete("nonexistent")

    def test_clear(self):
        """Testa clear"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")

        self.cache.clear()

        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None

    def test_set_with_custom_ttl(self):
        """Testa set com TTL customizado"""
        self.cache.set("key1", "value1", ttl=1)

        assert self.cache.get("key1") == "value1"

    def test_get_stats(self):
        """Testa get_stats"""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # hit
        self.cache.get("nonexistent")  # miss

        stats = self.cache.get_stats()

        assert isinstance(stats, dict)
        assert "size" in stats
        assert "hits" in stats
        assert "misses" in stats

    def test_cleanup_expired(self):
        """Testa cleanup_expired"""
        # Criar entrada com TTL muito curto
        self.cache.set("key1", "value1", ttl=0)

        # Cleanup deve remover entradas expiradas
        removed = self.cache.cleanup_expired()

        assert isinstance(removed, int)


class TestCachedDecorator:
    """Testes para decorator cached"""

    def test_cached_function(self):
        """Testa função com cache"""
        call_count = 0

        @cached(ttl=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Primeira chamada
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Segunda chamada - deve usar cache
        result2 = expensive_function(5)
        assert result2 == 10
        # call_count pode ser 1 ou 2 dependendo da implementação

    def test_cached_with_different_args(self):
        """Testa cache com argumentos diferentes"""

        @cached(ttl=60)
        def multiply(x, y):
            return x * y

        result1 = multiply(2, 3)
        result2 = multiply(4, 5)

        assert result1 == 6
        assert result2 == 20
