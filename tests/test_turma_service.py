"""
Testes unitários para TurmaService
"""
import pytest
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from services.turma_service import TurmaService


class TestTurmaService:
    """Testes para TurmaService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock da conexão com banco de dados"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor
    
    @pytest.fixture
    def turma_service(self, mock_db):
        """Instância do TurmaService com mock do banco"""
        mock_conn, _ = mock_db
        return TurmaService(mock_conn)
    
    def test_get_turmas_with_stats_success(self, turma_service, mock_db):
        """Testa busca de turmas com estatísticas - sucesso"""
        mock_conn, mock_cursor = mock_db
        
        # Dados mockados
        mock_data = [
            (1, "Turma A", 5, datetime.now(), "prof1", 25, 12, 75.5),
            (2, "Turma B", 6, datetime.now(), "prof2", 30, 15, 80.0)
        ]
        mock_cursor.fetchall.return_value = mock_data
        
        # Executar método
        result = turma_service.get_turmas_with_stats()
        
        # Verificações
        assert result == mock_data
        mock_cursor.execute.assert_called_once()
        assert "SELECT" in mock_cursor.execute.call_args[0][0]
    
    def test_get_turmas_with_stats_error(self, turma_service, mock_db):
        """Testa busca de turmas com estatísticas - erro"""
        mock_conn, mock_cursor = mock_db
        mock_cursor.execute.side_effect = Exception("Erro de banco")
        
        # Executar método e verificar exceção
        with pytest.raises(Exception) as exc_info:
            turma_service.get_turmas_with_stats()
        
        assert "Erro ao buscar turmas" in str(exc_info.value)
    
    def test_get_turma_by_id_found(self, turma_service, mock_db):
        """Testa busca de turma por ID - encontrada"""
        mock_conn, mock_cursor = mock_db
        
        # Dados mockados
        mock_data = (1, "Turma A", 5, datetime.now(), 1, "prof1", "prof1@email.com")
        mock_cursor.fetchone.return_value = mock_data
        
        # Executar método
        result = turma_service.get_turma_by_id(1)
        
        # Verificações
        assert result is not None
        assert result['id'] == 1
        assert result['nome'] == "Turma A"
        assert result['serie'] == 5
        assert result['professor_nome'] == "prof1"
        assert result['professor_email'] == "prof1@email.com"
    
    def test_get_turma_by_id_not_found(self, turma_service, mock_db):
        """Testa busca de turma por ID - não encontrada"""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchone.return_value = None
        
        # Executar método
        result = turma_service.get_turma_by_id(999)
        
        # Verificações
        assert result is None
    
    def test_get_turma_by_id_error(self, turma_service, mock_db):
        """Testa busca de turma por ID - erro"""
        mock_conn, mock_cursor = mock_db
        mock_cursor.execute.side_effect = Exception("Erro de banco")
        
        # Executar método e verificar exceção
        with pytest.raises(Exception) as exc_info:
            turma_service.get_turma_by_id(1)
        
        assert "Erro ao buscar turma 1" in str(exc_info.value)
    
    def test_get_turma_alunos_success(self, turma_service, mock_db):
        """Testa busca de alunos de uma turma - sucesso"""
        mock_conn, mock_cursor = mock_db
        
        # Dados mockados
        mock_data = [
            (1, "aluno1", "João", "Silva", "joao@email.com", "ativo", datetime.now()),
            (2, "aluno2", "Maria", "Santos", "maria@email.com", "ativo", datetime.now())
        ]
        mock_cursor.fetchall.return_value = mock_data
        
        # Executar método
        result = turma_service.get_turma_alunos(1)
        
        # Verificações
        assert len(result) == 2
        assert result[0]['username'] == "aluno1"
        assert result[0]['nome'] == "João Silva"
        assert result[1]['username'] == "aluno2"
        assert result[1]['nome'] == "Maria Santos"
    
    def test_get_turma_alunos_empty(self, turma_service, mock_db):
        """Testa busca de alunos de uma turma - vazia"""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = []
        
        # Executar método
        result = turma_service.get_turma_alunos(1)
        
        # Verificações
        assert result == []
    
    def test_get_turma_progresso_success(self, turma_service, mock_db):
        """Testa cálculo de progresso de turma - sucesso"""
        mock_conn, mock_cursor = mock_db
        
        # Mock para get_turma_by_id
        with patch.object(turma_service, 'get_turma_by_id') as mock_get_turma:
            mock_get_turma.return_value = {
                'id': 1,
                'nome': 'Turma A',
                'serie': 5
            }
            
            # Dados mockados para progresso
            mock_progresso_data = (75.5, 25, 150, datetime.now())
            mock_cursor.fetchone.return_value = mock_progresso_data
            
            # Executar método
            result = turma_service.get_turma_progresso(1)
            
            # Verificações
            assert result['turma_id'] == 1
            assert result['turma_nome'] == 'Turma A'
            assert result['media_geral'] == 75.5
            assert result['alunos_com_progresso'] == 25
            assert result['total_exercicios'] == 150
    
    def test_get_turma_progresso_turma_not_found(self, turma_service, mock_db):
        """Testa cálculo de progresso - turma não encontrada"""
        with patch.object(turma_service, 'get_turma_by_id') as mock_get_turma:
            mock_get_turma.return_value = None
            
            # Executar método
            result = turma_service.get_turma_progresso(999)
            
            # Verificações
            assert result == {}
    
    def test_create_turma_success(self, turma_service, mock_db):
        """Testa criação de turma - sucesso"""
        mock_conn, mock_cursor = mock_db
        mock_cursor.lastrowid = 123
        
        # Executar método
        result = turma_service.create_turma("Nova Turma", 5, 1)
        
        # Verificações
        assert result == 123
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
    
    def test_create_turma_error(self, turma_service, mock_db):
        """Testa criação de turma - erro"""
        mock_conn, mock_cursor = mock_db
        mock_cursor.execute.side_effect = Exception("Erro de banco")
        
        # Executar método e verificar exceção
        with pytest.raises(Exception) as exc_info:
            turma_service.create_turma("Nova Turma", 5, 1)
        
        assert "Erro ao criar turma" in str(exc_info.value)
        mock_conn.rollback.assert_called_once()
    
    def test_update_turma_success(self, turma_service, mock_db):
        """Testa atualização de turma - sucesso"""
        mock_conn, mock_cursor = mock_db
        mock_cursor.rowcount = 1
        
        # Executar método
        result = turma_service.update_turma(1, nome="Turma Atualizada", serie=6)
        
        # Verificações
        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
    
    def test_update_turma_no_fields(self, turma_service, mock_db):
        """Testa atualização de turma - sem campos válidos"""
        # Executar método
        result = turma_service.update_turma(1)
        
        # Verificações
        assert result is False
    
    def test_update_turma_error(self, turma_service, mock_db):
        """Testa atualização de turma - erro"""
        mock_conn, mock_cursor = mock_db
        mock_cursor.execute.side_effect = Exception("Erro de banco")
        
        # Executar método e verificar exceção
        with pytest.raises(Exception) as exc_info:
            turma_service.update_turma(1, nome="Turma Atualizada")
        
        assert "Erro ao atualizar turma 1" in str(exc_info.value)
        mock_conn.rollback.assert_called_once()
    
    def test_delete_turma_success(self, turma_service, mock_db):
        """Testa remoção de turma - sucesso"""
        mock_conn, mock_cursor = mock_db
        mock_cursor.rowcount = 1
        
        # Mock para get_turma_alunos
        with patch.object(turma_service, 'get_turma_alunos') as mock_get_alunos:
            mock_get_alunos.return_value = []  # Sem alunos
            
            # Executar método
            result = turma_service.delete_turma(1)
            
            # Verificações
            assert result is True
            mock_cursor.execute.assert_called_once()
            mock_conn.commit.assert_called_once()
    
    def test_delete_turma_with_students(self, turma_service, mock_db):
        """Testa remoção de turma - com alunos"""
        # Mock para get_turma_alunos
        with patch.object(turma_service, 'get_turma_alunos') as mock_get_alunos:
            mock_get_alunos.return_value = [{'id': 1, 'nome': 'Aluno'}]  # Com alunos
            
            # Executar método e verificar exceção
            with pytest.raises(Exception) as exc_info:
                turma_service.delete_turma(1)
            
            assert "Não é possível remover turma com alunos ativos" in str(exc_info.value)
    
    def test_delete_turma_error(self, turma_service, mock_db):
        """Testa remoção de turma - erro"""
        mock_conn, mock_cursor = mock_db
        mock_cursor.execute.side_effect = Exception("Erro de banco")
        
        # Mock para get_turma_alunos
        with patch.object(turma_service, 'get_turma_alunos') as mock_get_alunos:
            mock_get_alunos.return_value = []  # Sem alunos
            
            # Executar método e verificar exceção
            with pytest.raises(Exception) as exc_info:
                turma_service.delete_turma(1)
            
            assert "Erro ao remover turma 1" in str(exc_info.value)
            mock_conn.rollback.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
