#!/usr/bin/env python3
"""
Script para testar os decorators de autenticação
"""

import psycopg
from psycopg.rows import dict_row
from models_postgres import User

def test_decorators():
    """Testar os decorators de autenticação"""
    try:
        # Conectar ao banco
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        print("🔍 Testando decorators de autenticação...")
        
        # Testar professor
        print("\n👨‍🏫 Testando decorator @professor_required:")
        professor = User.authenticate('professor', 'prof123', db)
        if professor:
            print(f"✅ Professor autenticado: {professor.username}")
            print(f"🔑 É professor? {professor.is_professor}")
            print(f"🔑 É admin? {professor.is_admin}")
            print(f"🔐 Pode acessar dashboard professor? {professor.is_professor or professor.is_admin}")
        else:
            print("❌ Falha na autenticação do professor")
        
        # Testar aluno
        print("\n👨‍🎓 Testando decorator @aluno_required:")
        aluno = User.authenticate('aluno', 'aluno123', db)
        if aluno:
            print(f"✅ Aluno autenticado: {aluno.username}")
            print(f"🔑 É aluno? {aluno.is_aluno}")
            print(f"🔑 É admin? {aluno.is_admin}")
            print(f"🔐 Pode acessar dashboard aluno? {aluno.is_aluno}")
        else:
            print("❌ Falha na autenticação do aluno")
        
        # Testar admin
        print("\n👑 Testando decorator @admin_required:")
        admin = User.authenticate('admin', 'admin123', db)
        if admin:
            print(f"✅ Admin autenticado: {admin.username}")
            print(f"🔑 É admin? {admin.is_admin}")
            print(f"🔐 Pode acessar dashboard admin? {admin.is_admin}")
        else:
            print("❌ Falha na autenticação do admin")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    test_decorators()
