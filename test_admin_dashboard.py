#!/usr/bin/env python3
"""
Script para testar a função admin_dashboard
"""

import psycopg
from psycopg.rows import dict_row

def test_admin_dashboard():
    """Testar as consultas do admin dashboard"""
    
    try:
        # Conectar ao banco
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        print("🔍 Testando consultas do admin dashboard...")
        
        # Testar contagem de usuários por tipo
        print("\n1️⃣ Contando usuários por tipo:")
        cur = db.cursor()
        cur.execute('SELECT user_type, COUNT(*) FROM users GROUP BY user_type')
        user_stats_raw = cur.fetchall()
        user_stats = {row['user_type']: row['count'] for row in user_stats_raw}
        print(f"   Resultado: {user_stats}")
        
        # Testar contagem de turmas
        print("\n2️⃣ Contando turmas:")
        cur.execute('SELECT COUNT(*) FROM turmas')
        turmas_count = cur.fetchone()['count']
        print(f"   Resultado: {turmas_count}")
        
        # Testar contagem de aulas
        print("\n3️⃣ Contando aulas:")
        cur.execute('SELECT COUNT(*) FROM aulas')
        aulas_count = cur.fetchone()['count']
        print(f"   Resultado: {aulas_count}")
        
        # Testar contagem de matrículas
        print("\n4️⃣ Contando matrículas:")
        cur.execute('SELECT COUNT(*) FROM matriculas')
        matriculas_count = cur.fetchone()['count']
        print(f"   Resultado: {matriculas_count}")
        
        # Testar contagem de exercícios
        print("\n5️⃣ Contando exercícios:")
        cur.execute('SELECT COUNT(*) FROM exercicios')
        exercicios_count = cur.fetchone()['count']
        print(f"   Resultado: {exercicios_count}")
        
        cur.close()
        
        # Preparar dados como na função original
        stats = {
            'total_users': sum(user_stats.values()),
            'admin_users': user_stats.get('admin', 0),
            'professor_users': user_stats.get('professor', 0),
            'aluno_users': user_stats.get('aluno', 0),
            'total_turmas': turmas_count,
            'total_aulas': aulas_count,
            'total_matriculas': matriculas_count,
            'total_exercicios': exercicios_count
        }
        
        print(f"\n📊 Estatísticas finais:")
        print(f"   Total de usuários: {stats['total_users']}")
        print(f"   Admins: {stats['admin_users']}")
        print(f"   Professores: {stats['professor_users']}")
        print(f"   Alunos: {stats['aluno_users']}")
        print(f"   Total de turmas: {stats['total_turmas']}")
        print(f"   Total de aulas: {stats['total_aulas']}")
        print(f"   Total de matrículas: {stats['total_matriculas']}")
        print(f"   Total de exercícios: {stats['total_exercicios']}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    test_admin_dashboard()
