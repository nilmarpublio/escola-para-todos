#!/usr/bin/env python3
"""
Script para verificar todos os usuários existentes no banco
"""

import psycopg
from psycopg.rows import dict_row

def check_all_users():
    """Verificar todos os usuários existentes no banco"""
    try:
        # Conectar ao banco
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        print("🔍 Verificando todos os usuários no banco...")
        
        cur = db.cursor()
        
        # Listar todos os usuários
        cur.execute("""
            SELECT id, username, email, first_name, last_name, user_type, is_active 
            FROM users 
            ORDER BY user_type, username
        """)
        
        users = cur.fetchall()
        
        if users:
            print(f"✅ Encontrados {len(users)} usuários:")
            print()
            
            for user in users:
                status = "✅ Ativo" if user['is_active'] else "❌ Inativo"
                print(f"👤 ID: {user['id']}")
                print(f"   Username: {user['username']}")
                print(f"   Email: {user['email']}")
                print(f"   Nome: {user['first_name']} {user['last_name']}")
                print(f"   Tipo: {user['user_type']}")
                print(f"   Status: {status}")
                print()
        else:
            print("❌ Nenhum usuário encontrado no banco")
        
        cur.close()
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    check_all_users()
