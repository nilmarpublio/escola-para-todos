#!/usr/bin/env python3
"""
Script para testar se o Flask-Login está funcionando corretamente
"""

import psycopg
from psycopg.rows import dict_row
from models_postgres import User

def test_flask_login_simulation():
    """Simular o que o Flask-Login faz"""
    try:
        # Conectar ao banco
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        print("🔍 Testando simulação do Flask-Login...")
        
        # Simular login do professor
        print("\n👨‍🏫 Testando login do professor:")
        professor = User.authenticate('professor', 'prof123', db)
        if professor:
            print(f"✅ Professor autenticado: {professor.username}")
            print(f"🔑 É professor? {professor.is_professor}")
            print(f"🔐 Pode acessar dashboard? {professor.is_professor}")
        else:
            print("❌ Falha na autenticação do professor")
        
        # Simular login do aluno
        print("\n👨‍🎓 Testando login do aluno:")
        aluno = User.authenticate('aluno', 'aluno123', db)
        if aluno:
            print(f"✅ Aluno autenticado: {aluno.username}")
            print(f"🔑 É aluno? {aluno.is_aluno}")
            print(f"🔐 Pode acessar dashboard? {aluno.is_aluno}")
        else:
            print("❌ Falha na autenticação do aluno")
        
        # Simular login do admin
        print("\n👑 Testando login do admin:")
        admin = User.authenticate('admin', 'admin123', db)
        if admin:
            print(f"✅ Admin autenticado: {admin.username}")
            print(f"🔑 É admin? {admin.is_admin}")
            print(f"🔐 Pode acessar dashboard? {admin.is_admin}")
        else:
            print("❌ Falha na autenticação do admin")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    test_flask_login_simulation()
