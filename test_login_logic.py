#!/usr/bin/env python3
"""
Script para testar a lógica de login exatamente como na aplicação
"""

import psycopg
from psycopg.rows import dict_row
from models_postgres import User

def test_login_logic():
    """Testar a lógica de login exatamente como na aplicação"""
    try:
        # Conectar ao banco
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        print("🔍 Testando lógica de login da aplicação...")
        
        # Testar professor
        print("\n👨‍🏫 Testando login do professor:")
        professor = User.authenticate('professor', 'prof123', db)
        if professor:
            print(f"✅ Professor autenticado: {professor.username}")
            print(f"🔑 user.is_admin: {professor.is_admin}")
            print(f"🔑 user.is_professor: {professor.is_professor}")
            print(f"🔑 user.is_aluno: {professor.is_aluno}")
            
            # Simular a lógica da aplicação
            if professor.is_admin:
                print("🔄 Redirecionando para: admin_dashboard")
            elif professor.is_professor:
                print("🔄 Redirecionando para: professor_dashboard")
            else:
                print("🔄 Redirecionando para: student_dashboard")
        else:
            print("❌ Falha na autenticação do professor")
        
        # Testar aluno
        print("\n👨‍🎓 Testando login do aluno:")
        aluno = User.authenticate('aluno', 'aluno123', db)
        if aluno:
            print(f"✅ Aluno autenticado: {aluno.username}")
            print(f"🔑 user.is_admin: {aluno.is_admin}")
            print(f"🔑 user.is_professor: {aluno.is_professor}")
            print(f"🔑 user.is_aluno: {aluno.is_aluno}")
            
            # Simular a lógica da aplicação
            if aluno.is_admin:
                print("🔄 Redirecionando para: admin_dashboard")
            elif aluno.is_professor:
                print("🔄 Redirecionando para: professor_dashboard")
            else:
                print("🔄 Redirecionando para: student_dashboard")
        else:
            print("❌ Falha na autenticação do aluno")
        
        # Testar admin
        print("\n👑 Testando login do admin:")
        admin = User.authenticate('admin', 'admin123', db)
        if admin:
            print(f"✅ Admin autenticado: {admin.username}")
            print(f"🔑 user.is_admin: {admin.is_admin}")
            print(f"🔑 user.is_professor: {admin.is_professor}")
            print(f"🔑 user.is_aluno: {admin.is_aluno}")
            
            # Simular a lógica da aplicação
            if admin.is_admin:
                print("🔄 Redirecionando para: admin_dashboard")
            elif admin.is_professor:
                print("🔄 Redirecionando para: professor_dashboard")
            else:
                print("🔄 Redirecionando para: student_dashboard")
        else:
            print("❌ Falha na autenticação do admin")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    test_login_logic()
