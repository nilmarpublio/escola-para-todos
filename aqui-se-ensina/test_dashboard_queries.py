#!/usr/bin/env python3
"""
Script para testar as consultas SQL dos dashboards
"""

import psycopg
from psycopg.rows import dict_row

def test_dashboard_queries():
    """Testar as consultas SQL dos dashboards"""
    try:
        # Conectar ao banco
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        print("🔍 Testando consultas dos dashboards...")
        
        cur = db.cursor()
        
        # Testar consultas do dashboard do professor
        print("\n👨‍🏫 Testando consultas do dashboard do professor:")
        
        # 1. Contar aulas do professor (ID 2 = professor)
        try:
            cur.execute('SELECT COUNT(*) FROM aulas WHERE professor_id = %s', (2,))
            total_aulas = cur.fetchone()['count']
            print(f"  ✅ Total de aulas: {total_aulas}")
        except Exception as e:
            print(f"  ❌ Erro ao contar aulas: {e}")
        
        # 2. Contar turmas do professor
        try:
            cur.execute('SELECT COUNT(*) FROM turmas WHERE professor_id = %s', (2,))
            total_turmas = cur.fetchone()['count']
            print(f"  ✅ Total de turmas: {total_turmas}")
        except Exception as e:
            print(f"  ❌ Erro ao contar turmas: {e}")
        
        # 3. Contar alunos matriculados
        try:
            cur.execute('''
                SELECT COUNT(DISTINCT m.aluno_id) 
                FROM matriculas m 
                JOIN turmas t ON m.turma_id = t.id 
                WHERE t.professor_id = %s
            ''', (2,))
            total_alunos = cur.fetchone()['count']
            print(f"  ✅ Total de alunos: {total_alunos}")
        except Exception as e:
            print(f"  ❌ Erro ao contar alunos: {e}")
        
        # 4. Contar exercícios
        try:
            cur.execute('''
                SELECT COUNT(*) 
                FROM exercicios e 
                JOIN aulas a ON e.aula_id = a.id 
                WHERE a.professor_id = %s
            ''', (2,))
            total_exercicios = cur.fetchone()['count']
            print(f"  ✅ Total de exercícios: {total_exercicios}")
        except Exception as e:
            print(f"  ❌ Erro ao contar exercícios: {e}")
        
        # Testar consultas do dashboard do aluno
        print("\n👨‍🎓 Testando consultas do dashboard do aluno:")
        
        # 1. Contar aulas iniciadas
        try:
            cur.execute('''
                SELECT COUNT(*) 
                FROM progresso_alunos 
                WHERE aluno_id = %s AND status IN ('iniciada', 'em_progresso')
            ''', (3,))  # ID 3 = aluno
            aulas_iniciadas = cur.fetchone()['count']
            print(f"  ✅ Aulas iniciadas: {aulas_iniciadas}")
        except Exception as e:
            print(f"  ❌ Erro ao contar aulas iniciadas: {e}")
        
        # 2. Contar aulas concluídas
        try:
            cur.execute('''
                SELECT COUNT(*) 
                FROM progresso_alunos 
                WHERE aluno_id = %s AND status = 'concluida'
            ''', (3,))
            aulas_concluidas = cur.fetchone()['count']
            print(f"  ✅ Aulas concluídas: {aulas_concluidas}")
        except Exception as e:
            print(f"  ❌ Erro ao contar aulas concluídas: {e}")
        
        # 3. Contar pontos ganhos
        try:
            cur.execute('''
                SELECT COALESCE(SUM(pontos_ganhos), 0) 
                FROM respostas_alunos 
                WHERE aluno_id = %s
            ''', (3,))
            pontos_ganhos = cur.fetchone()['coalesce']
            print(f"  ✅ Pontos ganhos: {pontos_ganhos}")
        except Exception as e:
            print(f"  ❌ Erro ao contar pontos: {e}")
        
        cur.close()
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    test_dashboard_queries()
