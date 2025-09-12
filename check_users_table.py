#!/usr/bin/env python3
"""
Script para verificar a estrutura da tabela users
"""

import psycopg
from psycopg.rows import dict_row

def check_users_table():
    """Verificar a estrutura da tabela users"""
    
    try:
        # Conectar ao banco
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        print("🔍 Verificando estrutura da tabela users...")
        
        cur = db.cursor()
        
        # Verificar estrutura da tabela
        print("\n1️⃣ Estrutura da tabela users:")
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        for col in columns:
            print(f"   {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # Verificar dados da tabela
        print("\n2️⃣ Dados da tabela users:")
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        for user in users:
            print(f"   ID: {user['id']}, Username: {user['username']}, Type: {user['user_type']}, Active: {user['is_active']}")
        
        # Testar consulta específica
        print("\n3️⃣ Testando consulta GROUP BY:")
        cur.execute("SELECT user_type, COUNT(*) as count FROM users GROUP BY user_type")
        result = cur.fetchall()
        print(f"   Resultado bruto: {result}")
        
        # Verificar se há problema com o nome da coluna COUNT
        print("\n4️⃣ Verificando nomes das colunas:")
        for row in result:
            print(f"   user_type: {row['user_type']}, count: {row['count']}")
        
        cur.close()
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    check_users_table()
