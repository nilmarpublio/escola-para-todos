#!/usr/bin/env python3
"""
Script para testar se o user_loader está funcionando corretamente
"""

import psycopg
from psycopg.rows import dict_row
from models_postgres import User

def test_user_loader():
    """Testar se o user_loader está funcionando"""
    try:
        # Conectar ao banco
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        print("🔍 Testando user_loader...")
        
        # Simular o que o Flask-Login faz
        user_id = 1  # ID do admin
        
        # Testar get_by_id (que é usado no user_loader)
        user = User.get_by_id(user_id, db)
        
        if user:
            print(f"✅ Usuário carregado por ID: {user.username}")
            print(f"📝 Nome: {user.first_name} {user.last_name}")
            print(f"🏷️ Tipo: {user.user_type}")
            print(f"🔑 É admin? {user.is_admin}")
            print(f"👨‍🏫 É professor? {user.is_professor}")
            print(f"👨‍🎓 É aluno? {user.is_aluno}")
            print(f"🔐 Pode acessar admin? {user.can_access_admin_panel()}")
            print(f"👥 Pode gerenciar usuários? {user.can_manage_users()}")
        else:
            print("❌ Falha ao carregar usuário por ID")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    test_user_loader()
