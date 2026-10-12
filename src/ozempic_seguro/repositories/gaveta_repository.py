"""
Repositório de gavetas: manipulação de estado e histórico.

Implementa IGavetaRepository com lógica de persistência para gavetas.
"""

import sqlite3
from typing import Any

from ..core.logger import logger
from .connection import DatabaseConnection
from .interfaces import IGavetaRepository


class GavetaRepository(IGavetaRepository):
    """
    Repositório para operações de gavetas no banco de dados.

    Responsabilidades:
    - Gerenciar estado das gavetas (aberta/fechada)
    - Registrar histórico de operações
    - Consultar histórico com paginação
    """

    def __init__(self):
        self._db = DatabaseConnection.get_instance()

    def get_state(self, drawer_number: int) -> bool:
        """
        Retorna o estado atual de uma gaveta.

        Args:
            drawer_number: Drawer number

        Returns:
            True se aberta, False se fechada
        """
        self._db.execute(
            "SELECT esta_aberta FROM gavetas WHERE numero_gaveta = ?", (drawer_number,)
        )
        result = self._db.fetchone()
        return bool(result[0]) if result else False

    def set_state(
        self, drawer_number: int, state: bool, user_type: str, usuario_id: int | None = None
    ) -> tuple[bool, str]:
        """
        Define o estado de uma gaveta e registra no histórico.

        Args:
            drawer_number: Drawer number
            estado: True para abrir, False para fechar
            usuario_tipo: Tipo do usuário que realizou a ação
            usuario_id: ID do usuário (opcional)

        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            # Verifica se a gaveta existe
            self._db.execute(
                "SELECT id, esta_aberta FROM gavetas WHERE numero_gaveta = ?", (drawer_number,)
            )
            gaveta = self._db.fetchone()

            if not gaveta:
                # Cria nova gaveta
                self._db.execute(
                    "INSERT INTO gavetas (numero_gaveta, esta_aberta) VALUES (?, ?)",
                    (drawer_number, state),
                )
                gaveta_id = self._db.lastrowid()
                action = "aberta" if state else "fechada"
            else:
                gaveta_id = gaveta[0]
                previous_state = bool(gaveta[1])

                # Determina ação
                if state and not previous_state:
                    action = "aberta"
                elif not state and previous_state:
                    action = "fechada"
                else:
                    action = None

                # Atualiza se mudou
                if action:
                    self._db.execute(
                        "UPDATE gavetas SET esta_aberta = ?, ultima_atualizacao = CURRENT_TIMESTAMP WHERE id = ?",
                        (state, gaveta_id),
                    )

            # Registra histórico
            if action and usuario_id:
                self._db.execute(
                    "INSERT INTO historico_gavetas (gaveta_id, acao, usuario_id) VALUES (?, ?, ?)",
                    (gaveta_id, action, usuario_id),
                )
            elif action:
                self._db.execute(
                    "INSERT INTO historico_gavetas (gaveta_id, acao) VALUES (?, ?)",
                    (gaveta_id, action),
                )

            self._db.commit()
            return True, f"Gaveta {drawer_number} {action or 'sem alteração'}"

        except sqlite3.Error as e:
            logger.error(f"Database error setting drawer state: {e}")
            self._db.rollback()
            return False, f"Erro ao atualizar gaveta: {e!s}"

    def get_history(self, drawer_number: int, limit: int = 10) -> list[tuple]:
        """
        Retorna o histórico de uma gaveta.

        Args:
            drawer_number: Drawer number
            limit: Número máximo de registros

        Returns:
            Lista de tuplas (acao, username, data_hora)
        """
        self._db.execute(
            """
            SELECT h.acao, u.username, strftime('%d/%m/%Y %H:%M:%S', h.data_hora, 'localtime')
            FROM historico_gavetas h
            JOIN usuarios u ON h.usuario_id = u.id
            WHERE h.gaveta_id = (SELECT id FROM gavetas WHERE numero_gaveta = ?)
            ORDER BY h.data_hora DESC
            LIMIT ?
        """,
            (drawer_number, limit),
        )
        return self._db.fetchall()

    def get_history_paginated(
        self, drawer_number: int, offset: int = 0, limit: int = 20
    ) -> list[tuple]:
        """
        Retorna o histórico de uma gaveta com paginação.

        Args:
            drawer_number: Drawer number
            offset: Registros a pular
            limit: Número máximo de registros

        Returns:
            Lista de tuplas (acao, username, data_hora)
        """
        self._db.execute(
            """
            SELECT h.acao, u.username, strftime('%d/%m/%Y %H:%M:%S', h.data_hora, 'localtime')
            FROM historico_gavetas h
            JOIN usuarios u ON h.usuario_id = u.id
            WHERE h.gaveta_id = (SELECT id FROM gavetas WHERE numero_gaveta = ?)
            ORDER BY h.data_hora DESC
            LIMIT ? OFFSET ?
        """,
            (drawer_number, limit, offset),
        )
        return self._db.fetchall()

    def count_history(self, drawer_number: int) -> int:
        """
        Retorna o total de registros de histórico para uma gaveta.

        Args:
            drawer_number: Drawer number

        Returns:
            Número total de registros
        """
        self._db.execute(
            """
            SELECT COUNT(*)
            FROM historico_gavetas
            WHERE gaveta_id = (SELECT id FROM gavetas WHERE numero_gaveta = ?)
        """,
            (drawer_number,),
        )
        return self._db.fetchone()[0]

    def get_all_history(self) -> list[tuple]:
        """
        Retorna todo o histórico de todas as gavetas.

        Returns:
            Lista de tuplas (data_hora, numero_gaveta, acao, usuario)
        """
        self._db.execute(
            """
            SELECT
                strftime('%d/%m/%Y %H:%M:%S', h.data_hora, 'localtime') as data_hora,
                p.numero_gaveta,
                h.acao,
                u.username as usuario
            FROM historico_gavetas h
            JOIN gavetas p ON h.gaveta_id = p.id
            JOIN usuarios u ON h.usuario_id = u.id
            ORDER BY h.data_hora DESC
        """
        )
        return self._db.fetchall()

    def get_all_history_paginated(self, offset: int = 0, limit: int = 20) -> list[tuple]:
        """
        Retorna o histórico de todas as gavetas com paginação.

        Args:
            offset: Registros a pular
            limit: Número máximo de registros

        Returns:
            Lista de tuplas (data_hora, numero_gaveta, acao, usuario)
        """
        self._db.execute(
            """
            SELECT
                strftime('%d/%m/%Y %H:%M:%S', h.data_hora) as data_hora,
                p.numero_gaveta,
                h.acao,
                COALESCE(u.nome_completo, u.username, 'Sistema') as usuario
            FROM historico_gavetas h
            JOIN gavetas p ON h.gaveta_id = p.id
            LEFT JOIN usuarios u ON h.usuario_id = u.id
            ORDER BY h.data_hora DESC
            LIMIT ? OFFSET ?
        """,
            (limit, offset),
        )
        return self._db.fetchall()

    def count_all_history(self) -> int:
        """
        Retorna o número total de registros de histórico de todas as gavetas.

        Returns:
            Número total de registros
        """
        self._db.execute("SELECT COUNT(*) FROM historico_gavetas")
        return self._db.fetchone()[0]

    # Métodos da interface IRepository
    def find_by_id(self, entity_id: int) -> dict[str, Any] | None:
        """Implementação de IRepository.find_by_id"""
        self._db.execute(
            "SELECT id, numero_gaveta, esta_aberta FROM gavetas WHERE id = ?", (entity_id,)
        )
        row = self._db.fetchone()
        if row:
            return {"id": row[0], "numero_gaveta": row[1], "esta_aberta": bool(row[2])}
        return None

    def find_all(self) -> list[dict[str, Any]]:
        """Implementação de IRepository.find_all"""
        self._db.execute(
            "SELECT id, numero_gaveta, esta_aberta FROM gavetas ORDER BY numero_gaveta"
        )
        return [
            {"id": r[0], "numero_gaveta": r[1], "esta_aberta": bool(r[2])}
            for r in self._db.fetchall()
        ]

    def save(self, entity: dict[str, Any]) -> bool:
        """Implementação de IRepository.save"""
        if entity.get("id"):
            self._db.execute(
                "UPDATE gavetas SET esta_aberta = ? WHERE id = ?",
                (entity.get("esta_aberta", False), entity["id"]),
            )
        else:
            self._db.execute(
                "INSERT INTO gavetas (numero_gaveta, esta_aberta) VALUES (?, ?)",
                (entity.get("numero_gaveta", 0), entity.get("esta_aberta", False)),
            )
        self._db.commit()
        return True

    def delete(self, entity_id: int) -> bool:
        """Implementação de IRepository.delete"""
        self._db.execute("DELETE FROM gavetas WHERE id = ?", (entity_id,))
        self._db.commit()
        return self._db.cursor.rowcount > 0

    def exists(self, entity_id: int) -> bool:
        """Implementação de IRepository.exists"""
        return self.find_by_id(entity_id) is not None

    # Métodos da interface IGavetaRepository
    def find_by_numero(self, numero: int) -> dict[str, Any] | None:
        """Implementação de IGavetaRepository.find_by_numero"""
        self._db.execute(
            "SELECT id, numero_gaveta, esta_aberta FROM gavetas WHERE numero_gaveta = ?", (numero,)
        )
        row = self._db.fetchone()
        if row:
            return {"id": row[0], "numero_gaveta": row[1], "esta_aberta": bool(row[2])}
        return None

    def find_by_status(self, status: str) -> list[dict[str, Any]]:
        """Implementação de IGavetaRepository.find_by_status"""
        is_open = status.lower() in ("aberta", "open", "true", "1")
        self._db.execute(
            "SELECT id, numero_gaveta, esta_aberta FROM gavetas WHERE esta_aberta = ?", (is_open,)
        )
        return [
            {"id": r[0], "numero_gaveta": r[1], "esta_aberta": bool(r[2])}
            for r in self._db.fetchall()
        ]

    def find_by_user(self, user_id: int) -> list[dict[str, Any]]:
        """Implementação de IGavetaRepository.find_by_user"""
        self._db.execute(
            """
            SELECT DISTINCT g.id, g.numero_gaveta, g.esta_aberta
            FROM gavetas g
            JOIN historico_gavetas h ON g.id = h.gaveta_id
            WHERE h.usuario_id = ?
        """,
            (user_id,),
        )
        return [
            {"id": r[0], "numero_gaveta": r[1], "esta_aberta": bool(r[2])}
            for r in self._db.fetchall()
        ]

    def update_status(self, gaveta_id: int, status: str) -> bool:
        """Implementação de IGavetaRepository.update_status"""
        is_open = status.lower() in ("aberta", "open", "true", "1")
        self._db.execute("UPDATE gavetas SET esta_aberta = ? WHERE id = ?", (is_open, gaveta_id))
        self._db.commit()
        return self._db.cursor.rowcount > 0

    def assign_to_user(self, gaveta_id: int, user_id: int) -> bool:
        """Implementação de IGavetaRepository.assign_to_user - Registra no histórico"""
        self._db.execute(
            "INSERT INTO historico_gavetas (gaveta_id, acao, usuario_id) VALUES (?, ?, ?)",
            (gaveta_id, "atribuida", user_id),
        )
        self._db.commit()
        return True
