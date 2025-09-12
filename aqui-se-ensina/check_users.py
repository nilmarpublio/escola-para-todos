#!/usr/bin/env python3
"""
Script para verificar usuários no banco de dados PostgreSQL
"""

import psycopg
from psycopg.rows import dict_row

def check_users():
    """Verificar usuários no banco"""
    try:
        # Conectar ao banco
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        cur = db.cursor()
        
        # Verificar usuários
        cur.execute('SELECT id, username, email, first_name, last_name, user_type, is_active FROM users')
        users = cur.fetchall()
        
        print("👥 Usuários no banco de dados:")
        print("=" * 80)
        
        for user in users:
            print(f"ID: {user['id']}")
            print(f"Username: {user['username']}")
            print(f"Email: {user['email']}")
            print(f"Nome: {user['first_name']} {user['last_name']}")
            print(f"Tipo: {user['user_type']}")
            print(f"Ativo: {user['is_active']}")
            print("-" * 40)
        
        cur.close()
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    check_users()
