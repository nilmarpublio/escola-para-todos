"""
API REST para gerenciamento de turmas
"""
from flask import request, jsonify
from flask_restful import Resource, Api
from services.turma_service import TurmaService
from utils.database import get_db_manager
from auth import admin_required, professor_required
from flask_login import login_required, current_user
import logging

logger = logging.getLogger(__name__)


class TurmasAPI(Resource):
    """API para operações com turmas"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
    
    @login_required
    def get(self):
        """
        GET /api/turmas
        Lista todas as turmas com estatísticas
        """
        try:
            with self.db_manager.get_connection() as conn:
                service = TurmaService(conn)
                turmas = service.get_turmas_with_stats()
                
                # Converter para formato JSON
                turmas_data = []
                for turma in turmas:
                    turmas_data.append({
                        'id': turma[0],
                        'nome': turma[1],
                        'serie': turma[2],
                        'created_at': turma[3].isoformat() if turma[3] else None,
                        'professor': turma[4],
                        'total_alunos': turma[5] or 0,
                        'total_aulas': turma[6] or 0,
                        'media_progresso': float(turma[7]) if turma[7] else 0
                    })
                
                return {
                    'success': True,
                    'data': turmas_data,
                    'total': len(turmas_data)
                }, 200
                
        except Exception as e:
            logger.error(f"Erro na API de turmas: {e}")
            return {
                'success': False,
                'error': str(e)
            }, 500
    
    @admin_required
    def post(self):
        """
        POST /api/turmas
        Cria uma nova turma
        """
        try:
            data = request.get_json()
            
            if not data:
                return {
                    'success': False,
                    'error': 'Dados não fornecidos'
                }, 400
            
            # Validar campos obrigatórios
            required_fields = ['nome', 'serie', 'professor_id']
            for field in required_fields:
                if field not in data:
                    return {
                        'success': False,
                        'error': f'Campo obrigatório: {field}'
                    }, 400
            
            with self.db_manager.get_connection() as conn:
                service = TurmaService(conn)
                turma_id = service.create_turma(
                    nome=data['nome'],
                    serie=data['serie'],
                    professor_id=data['professor_id']
                )
                
                return {
                    'success': True,
                    'message': 'Turma criada com sucesso',
                    'turma_id': turma_id
                }, 201
                
        except Exception as e:
            logger.error(f"Erro ao criar turma: {e}")
            return {
                'success': False,
                'error': str(e)
            }, 500


class TurmaAPI(Resource):
    """API para operações com uma turma específica"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
    
    @login_required
    def get(self, turma_id):
        """
        GET /api/turmas/<id>
        Obtém detalhes de uma turma específica
        """
        try:
            with self.db_manager.get_connection() as conn:
                service = TurmaService(conn)
                turma = service.get_turma_by_id(turma_id)
                
                if not turma:
                    return {
                        'success': False,
                        'error': 'Turma não encontrada'
                    }, 404
                
                return {
                    'success': True,
                    'data': turma
                }, 200
                
        except Exception as e:
            logger.error(f"Erro ao buscar turma {turma_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }, 500
    
    @admin_required
    def put(self, turma_id):
        """
        PUT /api/turmas/<id>
        Atualiza uma turma existente
        """
        try:
            data = request.get_json()
            
            if not data:
                return {
                    'success': False,
                    'error': 'Dados não fornecidos'
                }, 400
            
            # Campos permitidos para atualização
            allowed_fields = ['nome', 'serie', 'professor_id']
            update_data = {k: v for k, v in data.items() if k in allowed_fields}
            
            if not update_data:
                return {
                    'success': False,
                    'error': 'Nenhum campo válido para atualização'
                }, 400
            
            with self.db_manager.get_connection() as conn:
                service = TurmaService(conn)
                success = service.update_turma(turma_id, **update_data)
                
                if success:
                    return {
                        'success': True,
                        'message': 'Turma atualizada com sucesso'
                    }, 200
                else:
                    return {
                        'success': False,
                        'error': 'Turma não encontrada ou não foi possível atualizar'
                    }, 404
                
        except Exception as e:
            logger.error(f"Erro ao atualizar turma {turma_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }, 500
    
    @admin_required
    def delete(self, turma_id):
        """
        DELETE /api/turmas/<id>
        Remove uma turma (soft delete)
        """
        try:
            with self.db_manager.get_connection() as conn:
                service = TurmaService(conn)
                success = service.delete_turma(turma_id)
                
                if success:
                    return {
                        'success': True,
                        'message': 'Turma removida com sucesso'
                    }, 200
                else:
                    return {
                        'success': False,
                        'error': 'Turma não encontrada ou não foi possível remover'
                    }, 404
                
        except Exception as e:
            logger.error(f"Erro ao remover turma {turma_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }, 500


class TurmaAlunosAPI(Resource):
    """API para operações com alunos de uma turma"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
    
    @login_required
    def get(self, turma_id):
        """
        GET /api/turmas/<id>/alunos
        Lista todos os alunos de uma turma
        """
        try:
            with self.db_manager.get_connection() as conn:
                service = TurmaService(conn)
                alunos = service.get_turma_alunos(turma_id)
                
                return {
                    'success': True,
                    'data': alunos,
                    'total': len(alunos)
                }, 200
                
        except Exception as e:
            logger.error(f"Erro ao buscar alunos da turma {turma_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }, 500


class TurmaProgressoAPI(Resource):
    """API para estatísticas de progresso de uma turma"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
    
    @login_required
    def get(self, turma_id):
        """
        GET /api/turmas/<id>/progresso
        Obtém estatísticas de progresso de uma turma
        """
        try:
            with self.db_manager.get_connection() as conn:
                service = TurmaService(conn)
                progresso = service.get_turma_progresso(turma_id)
                
                if not progresso:
                    return {
                        'success': False,
                        'error': 'Turma não encontrada'
                    }, 404
                
                return {
                    'success': True,
                    'data': progresso
                }, 200
                
        except Exception as e:
            logger.error(f"Erro ao buscar progresso da turma {turma_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }, 500


def register_turmas_api(api: Api):
    """
    Registra os endpoints de turmas na API
    
    Args:
        api (Api): Instância do Flask-RESTful API
    """
    api.add_resource(TurmasAPI, '/api/turmas')
    api.add_resource(TurmaAPI, '/api/turmas/<int:turma_id>')
    api.add_resource(TurmaAlunosAPI, '/api/turmas/<int:turma_id>/alunos')
    api.add_resource(TurmaProgressoAPI, '/api/turmas/<int:turma_id>/progresso')
