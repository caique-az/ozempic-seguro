"""
Testes para o sistema de cache.
"""

import time

from ozempic_seguro.core.cache import MemoryCache, cached, get_cache_stats, invalidate_cache


class TestMemoryCache:
    """Testes para MemoryCache"""

    def test_cache_set_and_get(self):
        """Testa set e get básicos"""
        cache = MemoryCache()

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Key não existente
        assert cache.get("nonexistent") is None

    def test_cache_ttl_expiration(self):
        """Testa expiração por TTL"""
        cache = MemoryCache(default_ttl=1)  # 1 segundo

        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1"

        # Espera expirar
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_cache_delete(self):
        """Testa remoção de entrada"""
        cache = MemoryCache()

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Remove
        assert cache.delete("key1") is True
        assert cache.get("key1") is None

        # Tenta remover novamente
        assert cache.delete("key1") is False

    def test_cache_clear(self):
        """Testa limpeza completa do cache"""
        cache = MemoryCache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None

    def test_cache_max_size(self):
        """Testa limite de tamanho do cache"""
        cache = MemoryCache(max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Adiciona quarto item (deve evictar o menos usado)
        cache.set("key4", "value4")

        # Verifica que tem apenas 3 items
        stats = cache.get_stats()
        assert stats["size"] == 3

    def test_cache_lru_eviction(self):
        """Testa evicção LRU"""
        cache = MemoryCache(max_size=2)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Acessa key1 para torná-lo mais recente
        cache.get("key1")

        # Adiciona key3 (deve evictar key2)
        cache.set("key3", "value3")

        assert cache.get("key1") == "value1"  # Ainda existe
        assert cache.get("key2") is None  # Foi evictado
        assert cache.get("key3") == "value3"  # Novo item

    def test_cache_stats(self):
        """Testa estatísticas do cache"""
        cache = MemoryCache()

        cache.set("key1", "value1")

        # Hit
        cache.get("key1")

        # Miss
        cache.get("nonexistent")

        stats = cache.get_stats()

        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["total_requests"] == 2
        assert "50.00%" in stats["hit_rate"]

    def test_cleanup_expired(self):
        """Testa limpeza de entradas expiradas"""
        cache = MemoryCache(default_ttl=1)

        cache.set("key1", "value1", ttl=1)
        cache.set("key2", "value2", ttl=10)
        cache.set("key3", "value3", ttl=1)

        time.sleep(1.1)

        removed = cache.cleanup_expired()

        assert removed == 2  # key1 e key3 expirados
        assert cache.get("key2") == "value2"  # key2 ainda válido


class TestCachedDecorator:
    """Testes para o decorator @cached"""

    def test_cached_function(self):
        """Testa função com cache"""
        call_count = 0

        @cached(ttl=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Primeira chamada - executa função
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Segunda chamada - retorna do cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Não incrementou

        # Chamada com argumento diferente - executa função
        result3 = expensive_function(3)
        assert result3 == 6
        assert call_count == 2

    def test_cached_with_kwargs(self):
        """Testa cache com kwargs"""
        call_count = 0

        @cached(ttl=10)
        def function_with_kwargs(a, b=1):
            nonlocal call_count
            call_count += 1
            return a + b

        result1 = function_with_kwargs(5, b=2)
        assert result1 == 7
        assert call_count == 1

        # Mesmos argumentos - cache
        result2 = function_with_kwargs(5, b=2)
        assert result2 == 7
        assert call_count == 1

        # Kwargs diferentes - nova execução
        result3 = function_with_kwargs(5, b=3)
        assert result3 == 8
        assert call_count == 2

    def test_cached_clear_cache(self):
        """Testa limpeza de cache de função específica"""
        call_count = 0

        @cached(ttl=10, key_prefix="test")
        def cached_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        cached_func(5)
        assert call_count == 1

        # Limpa cache da função
        cached_func.clear_cache()

        # Próxima chamada executa novamente
        cached_func(5)
        assert call_count == 2

    def test_invalidate_cache_pattern(self):
        """Testa invalidação por padrão"""
        from ozempic_seguro.core.cache import _global_cache

        # Limpa cache global antes do teste
        _global_cache.clear()

        @cached(ttl=10, key_prefix="user")
        def get_user(user_id):
            return f"User {user_id}"

        @cached(ttl=10, key_prefix="post")
        def get_post(post_id):
            return f"Post {post_id}"

        # Popula cache
        get_user(1)
        get_user(2)
        get_post(1)

        # Verifica tamanho antes de invalidar
        stats_before = get_cache_stats()
        assert stats_before["size"] == 3

        # Invalida apenas cache de usuários
        count = invalidate_cache("user")
        assert count == 2

        # Cache de posts ainda existe
        stats_after = get_cache_stats()
        assert stats_after["size"] == 1


class TestCacheEdgeCases:
    """Testes para casos extremos do cache"""

    def test_cache_none_value(self):
        """Testa cache de valor None"""
        cache = MemoryCache()
        cache.set("none_key", None)

        # Deve retornar None (valor armazenado)
        # Precisamos distinguir entre None armazenado e chave inexistente
        assert "none_key" in cache._cache

    def test_cache_complex_types(self):
        """Testa cache de tipos complexos"""
        cache = MemoryCache()

        # Lista
        cache.set("list", [1, 2, 3])
        assert cache.get("list") == [1, 2, 3]

        # Dict
        cache.set("dict", {"a": 1, "b": 2})
        assert cache.get("dict") == {"a": 1, "b": 2}

        # Tuple
        cache.set("tuple", (1, 2, 3))
        assert cache.get("tuple") == (1, 2, 3)

    def test_cache_overwrite(self):
        """Testa sobrescrita de valor"""
        cache = MemoryCache()

        cache.set("key", "value1")
        assert cache.get("key") == "value1"

        cache.set("key", "value2")
        assert cache.get("key") == "value2"

    def test_cache_hit_rate_zero_requests(self):
        """Testa hit rate com zero requisições"""
        cache = MemoryCache()
        stats = cache.get_stats()

        assert stats["hits"] == 0
        assert stats["misses"] == 0

    def test_cache_default_ttl(self):
        """Testa TTL padrão"""
        cache = MemoryCache(default_ttl=300)
        cache.set("key", "value")

        # Deve ter TTL definido
        assert cache.get("key") == "value"

    def test_get_cache_stats_function(self):
        """Testa função get_cache_stats"""
        stats = get_cache_stats()

        assert isinstance(stats, dict)
        assert "size" in stats
        assert "hits" in stats
        assert "misses" in stats
