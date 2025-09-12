#!/usr/bin/env python3
"""
Script para testar o usuário professor
"""

import psycopg
from psycopg.rows import dict_row
from models_postgres import User

def test_professor_user():
    """Testar usuário professor"""
    try:
        # Conectar ao banco
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        print("🔍 Testando usuário professor...")
        
        # Testar autenticação
        user = User.authenticate('professor', 'prof123', db)
        
        if user:
            print(f"✅ Usuário autenticado: {user.username}")
            print(f"📝 Nome: {user.first_name} {user.last_name}")
            print(f"🏷️ Tipo: {user.user_type}")
            print(f"🔑 É admin? {user.is_admin}")
            print(f"👨‍🏫 É professor? {user.is_professor}")
            print(f"👨‍🎓 É aluno? {user.is_aluno}")
            print(f"🔐 Pode acessar admin? {user.can_access_admin_panel()}")
            print(f"👥 Pode gerenciar usuários? {user.can_manage_users()}")
        else:
            print("❌ Falha na autenticação")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    test_professor_user()
