"""
Serviço para gerenciamento de turmas
Contém toda a lógica de negócio relacionada às turmas
"""
from typing import List, Dict, Optional, Tuple
import sqlite3
from datetime import datetime


class TurmaService:
    """Serviço para operações relacionadas às turmas"""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.db = db_connection
    
    def get_turmas_with_stats(self) -> List[Tuple]:
        """
        Busca todas as turmas com estatísticas completas
        
        Returns:
            List[Tuple]: Lista de tuplas com dados das turmas
        """
        try:
            cursor = self.db.cursor()
            
            query = """
                SELECT 
                    t.id, t.nome, t.serie, t.created_at,
                    u.username as professor,
                    COUNT(at.aluno_id) as total_alunos,
                    COUNT(a.id) as total_aulas,
                    AVG(p.pontuacao) as media_progresso
                FROM turmas t
                JOIN users u ON t.professor_id = u.id
                LEFT JOIN aluno_turma at ON t.id = at.turma_id 
                    AND (at.status = 'ativo' OR at.status IS NULL)
                LEFT JOIN aulas a ON t.serie = a.serie 
                    AND t.professor_id = a.professor_id
                LEFT JOIN progresso p ON a.id = p.aula_id
                GROUP BY t.id, t.nome, t.serie, t.created_at, u.username
                ORDER BY t.created_at DESC
            """
            
            cursor.execute(query)
            return cursor.fetchall()
            
        except Exception as e:
            raise Exception(f"Erro ao buscar turmas: {str(e)}")
    
    def get_turma_by_id(self, turma_id: int) -> Optional[Dict]:
        """
        Busca uma turma específica por ID
        
        Args:
            turma_id (int): ID da turma
            
        Returns:
            Optional[Dict]: Dados da turma ou None se não encontrada
        """
        try:
            cursor = self.db.cursor()
            
            query = """
                SELECT 
                    t.id, t.nome, t.serie, t.created_at, t.professor_id,
                    u.username as professor_nome,
                    u.email as professor_email
                FROM turmas t
                JOIN users u ON t.professor_id = u.id
                WHERE t.id = ?
            """
            
            cursor.execute(query, (turma_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'nome': result[1],
                    'serie': result[2],
                    'created_at': result[3],
                    'professor_id': result[4],
                    'professor_nome': result[5],
                    'professor_email': result[6]
                }
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao buscar turma {turma_id}: {str(e)}")
    
    def get_turma_alunos(self, turma_id: int) -> List[Dict]:
        """
        Busca todos os alunos de uma turma
        
        Args:
            turma_id (int): ID da turma
            
        Returns:
            List[Dict]: Lista de alunos da turma
        """
        try:
            cursor = self.db.cursor()
            
            query = """
                SELECT 
                    u.id, u.username, u.first_name, u.last_name, u.email,
                    at.status, at.created_at as inscricao_data
                FROM aluno_turma at
                JOIN users u ON at.aluno_id = u.id
                WHERE at.turma_id = ? AND (at.status = 'ativo' OR at.status IS NULL)
                ORDER BY u.first_name, u.last_name
            """
            
            cursor.execute(query, (turma_id,))
            results = cursor.fetchall()
            
            alunos = []
            for result in results:
                alunos.append({
                    'id': result[0],
                    'username': result[1],
                    'nome': f"{result[2]} {result[3]}",
                    'email': result[4],
                    'status': result[5],
                    'inscricao_data': result[6]
                })
            
            return alunos
            
        except Exception as e:
            raise Exception(f"Erro ao buscar alunos da turma {turma_id}: {str(e)}")
    
    def get_turma_progresso(self, turma_id: int) -> Dict:
        """
        Calcula estatísticas de progresso de uma turma
        
        Args:
            turma_id (int): ID da turma
            
        Returns:
            Dict: Estatísticas de progresso
        """
        try:
            cursor = self.db.cursor()
            
            # Buscar turma
            turma = self.get_turma_by_id(turma_id)
            if not turma:
                return {}
            
            # Buscar progresso dos alunos
            query = """
                SELECT 
                    AVG(p.pontuacao) as media_geral,
                    COUNT(DISTINCT p.aluno_id) as alunos_com_progresso,
                    COUNT(p.id) as total_exercicios,
                    MAX(p.created_at) as ultima_atividade
                FROM progresso p
                JOIN aulas a ON p.aula_id = a.id
                JOIN turmas t ON a.serie = t.serie AND a.professor_id = t.professor_id
                WHERE t.id = ?
            """
            
            cursor.execute(query, (turma_id,))
            result = cursor.fetchone()
            
            return {
                'turma_id': turma_id,
                'turma_nome': turma['nome'],
                'media_geral': result[0] or 0,
                'alunos_com_progresso': result[1] or 0,
                'total_exercicios': result[2] or 0,
                'ultima_atividade': result[3],
                'data_calculo': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Erro ao calcular progresso da turma {turma_id}: {str(e)}")
    
    def create_turma(self, nome: str, serie: int, professor_id: int) -> int:
        """
        Cria uma nova turma
        
        Args:
            nome (str): Nome da turma
            serie (int): Série/ano da turma
            professor_id (int): ID do professor responsável
            
        Returns:
            int: ID da turma criada
        """
        try:
            cursor = self.db.cursor()
            
            query = """
                INSERT INTO turmas (nome, serie, professor_id, created_at)
                VALUES (?, ?, ?, ?)
            """
            
            cursor.execute(query, (nome, serie, professor_id, datetime.now()))
            self.db.commit()
            
            return cursor.lastrowid
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Erro ao criar turma: {str(e)}")
    
    def update_turma(self, turma_id: int, **kwargs) -> bool:
        """
        Atualiza dados de uma turma
        
        Args:
            turma_id (int): ID da turma
            **kwargs: Campos a serem atualizados
            
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            if not kwargs:
                return False
            
            cursor = self.db.cursor()
            
            # Construir query dinamicamente
            fields = []
            values = []
            for key, value in kwargs.items():
                if key in ['nome', 'serie', 'professor_id']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return False
            
            values.append(turma_id)
            query = f"UPDATE turmas SET {', '.join(fields)} WHERE id = ?"
            
            cursor.execute(query, values)
            self.db.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Erro ao atualizar turma {turma_id}: {str(e)}")
    
    def delete_turma(self, turma_id: int) -> bool:
        """
        Remove uma turma (soft delete)
        
        Args:
            turma_id (int): ID da turma
            
        Returns:
            bool: True se removida com sucesso
        """
        try:
            cursor = self.db.cursor()
            
            # Verificar se há alunos ativos
            alunos = self.get_turma_alunos(turma_id)
            if alunos:
                raise Exception("Não é possível remover turma com alunos ativos")
            
            # Soft delete - marcar como inativa
            query = "UPDATE turmas SET is_active = 0 WHERE id = ?"
            cursor.execute(query, (turma_id,))
            self.db.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Erro ao remover turma {turma_id}: {str(e)}")
