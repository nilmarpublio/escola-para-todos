#!/usr/bin/env python3
"""
Script para verificar se as tabelas necessárias existem no banco
"""

import psycopg
from psycopg.rows import dict_row

def test_tables():
    """Verificar se as tabelas necessárias existem"""
    try:
        # Conectar ao banco
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        print("🔍 Verificando tabelas no banco...")
        
        cur = db.cursor()
        
        # Listar todas as tabelas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        print(f"📋 Tabelas encontradas ({len(tables)}):")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Verificar tabelas específicas que estou usando
        required_tables = [
            'users', 'turmas', 'aulas', 'matriculas', 'exercicios',
            'progresso_alunos', 'respostas_alunos'
        ]
        
        print(f"\n🔍 Verificando tabelas necessárias:")
        for table in required_tables:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, (table,))
            
            exists = cur.fetchone()['exists']
            status = "✅" if exists else "❌"
            print(f"  {status} {table}")
        
        cur.close()
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    test_tables()
