#!/usr/bin/env python
"""
Script de teste para verificar autenticação.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ozempic_seguro.repositories.database import DatabaseManager
from ozempic_seguro.repositories.user_repository import UserRepository
from ozempic_seguro.repositories.security import verify_password
from ozempic_seguro.session.session_manager import SessionManager


def test_login():
    print("=== TESTE DE AUTENTICAÇÃO ===\n")

    # Teste 1: Verificar usuário no banco
    print("1. Verificando usuário no banco de dados...")
    db = DatabaseManager()
    db.cursor.execute("SELECT * FROM usuarios WHERE username = '00'")
    user = db.cursor.fetchone()

    if user:
        print(f"   ✓ Usuário '00' encontrado")
        print(f"   - ID: {user[0]}")
        print(f"   - Username: {user[1]}")
        print(f"   - Hash: {user[2][:20]}...")
        print(f"   - Tipo: {user[4]}")
        print(f"   - Ativo: {user[5]}")
    else:
        print("   ✗ Usuário '00' NÃO encontrado!")
        return

    # Teste 2: Verificar senha
    print("\n2. Verificando senha...")
    senha_correta = verify_password("1234", user[2])
    print(f"   - Senha '1234' está {'✓ CORRETA' if senha_correta else '✗ INCORRETA'}")

    # Teste 3: Testar método authenticate_user do UserRepository
    print("\n3. Testando método authenticate_user...")
    user_repo = UserRepository()
    result = user_repo.authenticate_user("00", "1234")
    if result:
        print(f"   ✓ Autenticação bem-sucedida!")
        print(f"   - Usuário: {result['username']}")
        print(f"   - Tipo: {result['tipo']}")
    else:
        print("   ✗ Autenticação FALHOU!")

    # Teste 4: Verificar SessionManager
    print("\n4. Verificando SessionManager...")
    session = SessionManager.get_instance()
    from ozempic_seguro.config import Config

    print(f"   - MAX_LOGIN_ATTEMPTS: {Config.Security.MAX_LOGIN_ATTEMPTS}")
    print(f"   - LOCKOUT_DURATION: {Config.Security.LOCKOUT_DURATION_MINUTES} minutos")

    # Teste 5: Simular tentativas
    print("\n5. Simulando tentativas de login...")
    for i in range(4):
        session.increment_login_attempts("teste_user")
        remaining = session.get_remaining_attempts("teste_user")
        is_locked = session.is_user_blocked("teste_user")
        print(f"   - Tentativa {i+1}: {remaining} restantes, Bloqueado: {is_locked}")

    print("\n=== FIM DO TESTE ===")


if __name__ == "__main__":
    test_login()
