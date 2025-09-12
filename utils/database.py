"""
Utilitários para operações de banco de dados
"""
import sqlite3
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gerenciador de conexões com banco de dados"""
    
    def __init__(self, database_path: str = 'escola_para_todos.db'):
        self.database_path = database_path
    
    @contextmanager
    def get_connection(self):
        """
        Context manager para conexões com banco de dados
        
        Yields:
            sqlite3.Connection: Conexão com o banco
        """
        conn = None
        try:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            logger.error(f"Erro na conexão com banco: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Executa uma query SELECT e retorna os resultados
        
        Args:
            query (str): Query SQL a ser executada
            params (tuple): Parâmetros da query
            
        Returns:
            List[Dict[str, Any]]: Lista de resultados como dicionários
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Converter para lista de dicionários
            return [dict(row) for row in results]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Executa uma query de UPDATE/INSERT/DELETE
        
        Args:
            query (str): Query SQL a ser executada
            params (tuple): Parâmetros da query
            
        Returns:
            int: Número de linhas afetadas
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Executa a mesma query com múltiplos conjuntos de parâmetros
        
        Args:
            query (str): Query SQL a ser executada
            params_list (List[tuple]): Lista de parâmetros
            
        Returns:
            int: Número total de linhas afetadas
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
    
    def table_exists(self, table_name: str) -> bool:
        """
        Verifica se uma tabela existe
        
        Args:
            table_name (str): Nome da tabela
            
        Returns:
            bool: True se a tabela existe
        """
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        results = self.execute_query(query, (table_name,))
        return len(results) > 0
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Obtém informações sobre a estrutura de uma tabela
        
        Args:
            table_name (str): Nome da tabela
            
        Returns:
            List[Dict[str, Any]]: Informações das colunas
        """
        query = "PRAGMA table_info(?)"
        return self.execute_query(query, (table_name,))
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Cria backup do banco de dados
        
        Args:
            backup_path (str): Caminho para o arquivo de backup
            
        Returns:
            bool: True se backup criado com sucesso
        """
        try:
            import shutil
            shutil.copy2(self.database_path, backup_path)
            logger.info(f"Backup criado em: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return False
    
    def optimize_database(self) -> bool:
        """
        Otimiza o banco de dados (VACUUM e ANALYZE)
        
        Returns:
            bool: True se otimização realizada com sucesso
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("VACUUM")
                cursor.execute("ANALYZE")
                logger.info("Banco de dados otimizado")
                return True
        except Exception as e:
            logger.error(f"Erro ao otimizar banco: {e}")
            return False


def get_db_manager() -> DatabaseManager:
    """
    Factory function para obter instância do DatabaseManager
    
    Returns:
        DatabaseManager: Instância configurada
    """
    return DatabaseManager()


def safe_sql_string(value: str) -> str:
    """
    Sanitiza string para uso em queries SQL (básico)
    
    Args:
        value (str): String a ser sanitizada
        
    Returns:
        str: String sanitizada
    """
    if not isinstance(value, str):
        return str(value)
    
    # Remover caracteres perigosos
    dangerous_chars = ["'", '"', ';', '--', '/*', '*/']
    for char in dangerous_chars:
        value = value.replace(char, '')
    
    return value.strip()


def build_where_clause(conditions: Dict[str, Any]) -> tuple:
    """
    Constrói cláusula WHERE dinamicamente
    
    Args:
        conditions (Dict[str, Any]): Condições como dicionário
        
    Returns:
        tuple: (clause, params) onde clause é a string SQL e params são os valores
    """
    if not conditions:
        return "", ()
    
    clauses = []
    params = []
    
    for field, value in conditions.items():
        if value is not None:
            if isinstance(value, (list, tuple)):
                placeholders = ','.join(['?' for _ in value])
                clauses.append(f"{field} IN ({placeholders})")
                params.extend(value)
            else:
                clauses.append(f"{field} = ?")
                params.append(value)
    
    if clauses:
        return f"WHERE {' AND '.join(clauses)}", tuple(params)
    
    return "", ()


def paginate_query(base_query: str, page: int = 1, per_page: int = 20) -> str:
    """
    Adiciona paginação a uma query SQL
    
    Args:
        base_query (str): Query base
        page (int): Número da página (começa em 1)
        per_page (int): Itens por página
        
    Returns:
        str: Query com LIMIT e OFFSET
    """
    offset = (page - 1) * per_page
    return f"{base_query} LIMIT {per_page} OFFSET {offset}"
