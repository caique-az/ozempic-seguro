#!/usr/bin/env python
"""
Script para verificar os usuários criados.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ozempic_seguro.repositories.database import DatabaseManager
from ozempic_seguro.repositories.user_repository import UserRepository


def test_users():
    print("=== VERIFICANDO USUÁRIOS ===\n")

    db = DatabaseManager()
    user_repo = UserRepository()

    # Lista todos os usuários
    db.cursor.execute("SELECT id, username, nome_completo, tipo, ativo FROM usuarios ORDER BY id")
    users = db.cursor.fetchall()

    print(f"Total de usuários: {len(users)}\n")

    for user in users:
        print(f"ID: {user[0]}")
        print(f"  Username: {user[1]}")
        print(f"  Nome: {user[2]}")
        print(f"  Tipo: {user[3]}")
        print(f"  Ativo: {'Sim' if user[4] else 'Não'}")
        print()

    # Testa login do admin usando UserRepository
    print("Testando login do admin (00/1234)...")
    result = user_repo.authenticate_user("00", "1234")
    if result:
        print(f"  ✓ Login bem-sucedido! Tipo: {result['tipo']}")
    else:
        print("  ✗ Login falhou!")

    # Testa login do técnico usando UserRepository
    print("\nTestando login do técnico (01/1234)...")
    result = user_repo.authenticate_user("01", "1234")
    if result:
        print(f"  ✓ Login bem-sucedido! Tipo: {result['tipo']}")
    else:
        print("  ✗ Login falhou!")


if __name__ == "__main__":
    test_users()
