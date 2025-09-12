#!/usr/bin/env python3
"""
Script para verificar especificamente o usuário aluno no banco
"""

import psycopg
from psycopg.rows import dict_row

def check_aluno_user():
    """Verificar especificamente o usuário aluno"""
    try:
        # Conectar ao banco
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        print("🔍 Verificando usuário aluno no banco...")
        
        cur = db.cursor()
        
        # Verificar se o usuário aluno existe
        cur.execute("SELECT * FROM users WHERE username = 'aluno'")
        aluno = cur.fetchone()
        
        if aluno:
            print(f"✅ Usuário aluno encontrado:")
            print(f"  ID: {aluno['id']}")
            print(f"  Username: {aluno['username']}")
            print(f"  Email: {aluno['email']}")
            print(f"  Nome: {aluno['first_name']} {aluno['last_name']}")
            print(f"  Tipo: {aluno['user_type']}")
            print(f"  Ativo: {aluno['is_active']}")
            print(f"  Senha hash: {aluno['password_hash'][:50]}...")
        else:
            print("❌ Usuário aluno não encontrado!")
            
            # Listar todos os usuários para debug
            print("\n📋 Todos os usuários no banco:")
            cur.execute("SELECT id, username, email, user_type FROM users")
            users = cur.fetchall()
            for user in users:
                print(f"  - ID {user['id']}: {user['username']} ({user['user_type']}) - {user['email']}")
        
        cur.close()
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    check_aluno_user()
