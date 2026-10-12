#!/usr/bin/env python
"""
Script para resetar a senha do admin para o formato bcrypt.

As credenciais são lidas das variáveis de ambiente:
  OZEMPIC_ADMIN_USERNAME  (padrão: "00")
  OZEMPIC_ADMIN_PASSWORD  (padrão: "admin@2025")
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ozempic_seguro.repositories.database import DatabaseManager
from ozempic_seguro.repositories.security import hash_password


def reset_admin_password():
    print("=== RESET DE SENHA DO ADMIN ===\n")

    admin_username = os.getenv("OZEMPIC_ADMIN_USERNAME", "00")
    admin_password = os.getenv("OZEMPIC_ADMIN_PASSWORD", "admin@2025")

    db = DatabaseManager()

    # Gera novo hash bcrypt a partir da variável de ambiente
    new_hash = hash_password(admin_password)
    print(f"Novo hash gerado (bcrypt): {new_hash[:20]}...")

    # Atualiza senha do usuário conforme variável de ambiente
    db.cursor.execute(
        "UPDATE usuarios SET senha_hash = ? WHERE username = ?", (new_hash, admin_username)
    )
    db.conn.commit()

    print("Senha do admin atualizada com sucesso!")
    print("\nCredenciais:")
    print(f"  Usuário: {admin_username}")
    print(f"  Senha: {admin_password}")

    # Verifica
    result = db.autenticar_usuario(admin_username, admin_password)
    if result:
        print("\nTeste de login bem-sucedido!")
    else:
        print("\nErro no teste de login!")


if __name__ == "__main__":
    reset_admin_password()
