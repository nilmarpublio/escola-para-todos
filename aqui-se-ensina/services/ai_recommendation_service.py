import math
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import psycopg
from psycopg.rows import dict_row
import os

@dataclass
class LearningPath:
    """Representa um caminho de aprendizado"""
    aula_id: int
    titulo: str
    descricao: str
    dificuldade: str
    pontuacao: float
    razao: str
    ordem: int

@dataclass
class StudentProfile:
    """Perfil do aluno com métricas de desempenho"""
    aluno_id: int
    progresso_medio: float
    aulas_concluidas: int
    pontos_totais: int
    streak_atual: int
    nivel_atual: str
    areas_fortes: List[str]
    areas_fracas: List[str]
    ultima_atividade: datetime

class AIRecommendationService:
    """Serviço de IA para recomendações personalizadas"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
    
    def _get_db_connection(self):
        """Obtém conexão com o banco PostgreSQL"""
        return psycopg.connect(self.db_url, row_factory=dict_row)
    
    def get_student_profile(self, aluno_id: int) -> StudentProfile:
        """Obtém o perfil completo do aluno"""
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Buscar métricas básicas do aluno
                    cur.execute("""
                        SELECT 
                            u.id,
                            COALESCE(AVG(pa.progresso), 0) as progresso_medio,
                            COUNT(CASE WHEN pa.status = 'concluida' THEN 1 END) as aulas_concluidas,
                            COALESCE(SUM(pa.pontos), 0) as pontos_totais,
                            MAX(pa.updated_at) as ultima_atividade
                        FROM users u
                        LEFT JOIN progresso_alunos pa ON pa.aluno_id = u.id
                        WHERE u.id = %s AND u.tipo = 'aluno'
                        GROUP BY u.id
                    """, (aluno_id,))
                    
                    result = cur.fetchone()
                    if not result:
                        return None
                    
                    # Calcular streak atual (dias consecutivos de atividade)
                    cur.execute("""
                        SELECT COUNT(DISTINCT DATE(pa.updated_at)) as streak
                        FROM progresso_alunos pa
                        WHERE pa.aluno_id = %s 
                        AND pa.updated_at >= CURRENT_DATE - INTERVAL '30 days'
                        ORDER BY pa.updated_at DESC
                    """, (aluno_id,))
                    
                    streak_result = cur.fetchone()
                    streak_atual = streak_result['streak'] if streak_result else 0
                    
                    # Determinar nível atual
                    progresso_medio = result['progresso_medio'] or 0
                    aulas_concluidas = result['aulas_concluidas'] or 0
                    nivel_atual = self._determine_level(progresso_medio, aulas_concluidas)
                    
                    # Analisar áreas fortes e fracas
                    areas_fortes, areas_fracas = self._analyze_learning_areas(aluno_id)
                    
                    return StudentProfile(
                        aluno_id=result['id'],
                        progresso_medio=progresso_medio,
                        aulas_concluidas=aulas_concluidas,
                        pontos_totais=result['pontos_totais'] or 0,
                        streak_atual=streak_atual,
                        nivel_atual=nivel_atual,
                        areas_fortes=areas_fortes,
                        areas_fracas=areas_fracas,
                        ultima_atividade=result['ultima_atividade']
                    )
        except Exception as e:
            print(f"Erro ao obter perfil do aluno: {e}")
            return None
    
    def _analyze_learning_areas(self, aluno_id: int) -> Tuple[List[str], List[str]]:
        """Analisa áreas fortes e fracas do aluno"""
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Buscar performance por turma (área de conhecimento)
                    cur.execute("""
                        SELECT 
                            t.nome as turma_nome,
                            AVG(pa.progresso) as media_progresso,
                            COUNT(CASE WHEN pa.status = 'concluida' THEN 1 END) as aulas_concluidas
                        FROM progresso_alunos pa
                        JOIN aulas a ON a.id = pa.aula_id
                        JOIN turmas t ON t.id = a.turma_id
                        WHERE pa.aluno_id = %s
                        GROUP BY t.id, t.nome
                        ORDER BY media_progresso DESC
                    """, (aluno_id,))
                    
                    areas = cur.fetchall()
                    
                    areas_fortes = []
                    areas_fracas = []
                    
                    for area in areas:
                        if area['media_progresso'] and area['media_progresso'] > 70:
                            areas_fortes.append(area['turma_nome'])
                        elif area['media_progresso'] and area['media_progresso'] < 50:
                            areas_fracas.append(area['turma_nome'])
                    
                    return areas_fortes, areas_fracas
        except Exception as e:
            print(f"Erro ao analisar áreas de aprendizado: {e}")
            return [], []
    
    def _determine_level(self, progresso_medio: float, aulas_concluidas: int) -> str:
        """Determina o nível atual do aluno"""
        if aulas_concluidas < 5:
            return "Iniciante"
        elif progresso_medio < 50:
            return "Básico"
        elif progresso_medio < 75:
            return "Intermediário"
        elif aulas_concluidas > 20:
            return "Avançado"
        else:
            return "Intermediário"
    
    def get_personalized_recommendations(self, aluno_id: int, limit: int = 10) -> List[LearningPath]:
        """Obtém recomendações personalizadas para o aluno"""
        try:
            profile = self.get_student_profile(aluno_id)
            if not profile:
                return []
            
            with self._get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Buscar aulas disponíveis
                    cur.execute("""
                        SELECT 
                            a.id,
                            a.titulo,
                            a.descricao,
                            a.dificuldade,
                            t.nome as turma_nome,
                            COUNT(pa.id) as total_alunos,
                            AVG(pa.progresso) as media_progresso
                        FROM aulas a
                        JOIN turmas t ON t.id = a.turma_id
                        LEFT JOIN progresso_alunos pa ON pa.aula_id = a.id
                        WHERE a.id NOT IN (
                            SELECT aula_id FROM progresso_alunos 
                            WHERE aluno_id = %s AND status = 'concluida'
                        )
                        GROUP BY a.id, a.titulo, a.descricao, a.dificuldade, t.nome
                        ORDER BY a.created_at DESC
                    """, (aluno_id,))
                    
                    aulas = cur.fetchall()
                    
                    # Calcular pontuação para cada aula
                    recomendacoes = []
                    for i, aula in enumerate(aulas):
                        score = self._calculate_recommendation_score(aula, profile)
                        razao = self._generate_recommendation_reason(aula, profile, score)
                        
                        recomendacoes.append(LearningPath(
                            aula_id=aula['id'],
                            titulo=aula['titulo'],
                            descricao=aula['descricao'],
                            dificuldade=aula['dificuldade'],
                            pontuacao=score,
                            razao=razao,
                            ordem=i + 1
                        ))
                    
                    # Ordenar por pontuação e retornar top N
                    recomendacoes.sort(key=lambda x: x.pontuacao, reverse=True)
                    return recomendacoes[:limit]
                    
        except Exception as e:
            print(f"Erro ao obter recomendações: {e}")
            return []
    
    def _calculate_recommendation_score(self, aula: dict, profile: StudentProfile) -> float:
        """Calcula pontuação para uma aula baseada no perfil do aluno"""
        score = 0.0
        
        # Pontuação base na dificuldade
        if self._is_difficulty_appropriate(aula['dificuldade'], profile.nivel_atual):
            score += 30
        
        # Pontuação por área de melhoria
        if aula['turma_nome'] in profile.areas_fracas:
            score += 25
        
        # Pontuação por popularidade
        if aula['total_alunos'] and aula['total_alunos'] > 10:
            score += 15
        
        # Pontuação por recência
        score += 10
        
        # Pontuação por streak (manter engajamento)
        if profile.streak_atual > 0:
            score += 20
        
        return score
    
    def _is_difficulty_appropriate(self, dificuldade: str, nivel_aluno: str) -> bool:
        """Verifica se a dificuldade é apropriada para o nível do aluno"""
        niveis = {
            'Iniciante': ['Fácil'],
            'Básico': ['Fácil', 'Médio'],
            'Intermediário': ['Médio', 'Difícil'],
            'Avançado': ['Difícil', 'Muito Difícil']
        }
        
        return dificuldade in niveis.get(nivel_aluno, ['Médio'])
    
    def _generate_recommendation_reason(self, aula: dict, profile: StudentProfile, score: float) -> str:
        """Gera razão para a recomendação"""
        razoes = []
        
        if aula['turma_nome'] in profile.areas_fracas:
            razoes.append("Área para melhorar")
        
        if self._is_difficulty_appropriate(aula['dificuldade'], profile.nivel_atual):
            razoes.append("Dificuldade adequada")
        
        if profile.streak_atual > 0:
            razoes.append("Manter progresso")
        
        if aula['total_alunos'] and aula['total_alunos'] > 10:
            razoes.append("Popular entre alunos")
        
        return ", ".join(razoes) if razoes else "Recomendação personalizada"
    
    def get_adaptive_learning_path(self, aluno_id: int, objetivo: str = None) -> List[LearningPath]:
        """Gera caminho de aprendizado adaptativo"""
        recomendacoes = self.get_personalized_recommendations(aluno_id, limit=15)
        
        # Organizar em sequência progressiva
        caminho = []
        for i, rec in enumerate(recomendacoes):
            rec.ordem = i + 1
            caminho.append(rec)
        
        return caminho
    
    def get_learning_insights(self, aluno_id: int) -> Dict:
        """Obtém insights de aprendizado para o aluno"""
        try:
            profile = self.get_student_profile(aluno_id)
            if not profile:
                return {}
            
            with self._get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Tendência de progresso (últimos 7 dias)
                    cur.execute("""
                        SELECT 
                            DATE(pa.updated_at) as data,
                            AVG(pa.progresso) as media_dia
                        FROM progresso_alunos pa
                        WHERE pa.aluno_id = %s 
                        AND pa.updated_at >= CURRENT_DATE - INTERVAL '7 days'
                        GROUP BY DATE(pa.updated_at)
                        ORDER BY data
                    """, (aluno_id,))
                    
                    tendencia = cur.fetchall()
                    
                    # Próximo objetivo sugerido
                    proximo_objetivo = self._suggest_next_goal(profile)
                    
                    return {
                        'perfil': {
                            'nivel': profile.nivel_atual,
                            'progresso_medio': round(profile.progresso_medio, 1),
                            'aulas_concluidas': profile.aulas_concluidas,
                            'pontos_totais': profile.pontos_totais,
                            'streak_atual': profile.streak_atual
                        },
                        'areas': {
                            'fortes': profile.areas_fortes,
                            'fracas': profile.areas_fracas
                        },
                        'tendencia': [
                            {
                                'data': str(t['data']),
                                'progresso': round(t['media_dia'] or 0, 1)
                            } for t in tendencia
                        ],
                        'proximo_objetivo': proximo_objetivo,
                        'ultima_atividade': str(profile.ultima_atividade) if profile.ultima_atividade else None
                    }
                    
        except Exception as e:
            print(f"Erro ao obter insights: {e}")
            return {}
    
    def _suggest_next_goal(self, profile: StudentProfile) -> str:
        """Sugere próximo objetivo para o aluno"""
        if profile.aulas_concluidas < 5:
            return "Complete suas primeiras 5 aulas"
        elif profile.progresso_medio < 60:
            return "Melhore seu progresso médio para 60%"
        elif profile.streak_atual < 3:
            return "Mantenha uma sequência de 3 dias de estudo"
        elif profile.areas_fracas:
            return f"Foque em melhorar: {', '.join(profile.areas_fracas[:2])}"
        else:
            return "Continue explorando novos conteúdos"


def get_recommendations_for_student(aluno_id: int, limit: int = 10) -> List[LearningPath]:
    """Função helper para obter recomendações"""
    service = AIRecommendationService()
    return service.get_personalized_recommendations(aluno_id, limit)


def get_learning_insights_for_student(aluno_id: int) -> Dict:
    """Função helper para obter insights"""
    service = AIRecommendationService()
    return service.get_learning_insights(aluno_id)
