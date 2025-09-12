#!/usr/bin/env python3
"""
Script para testar especificamente a autenticação do usuário aluno
"""

import psycopg
from psycopg.rows import dict_row
from models_postgres import User

def test_aluno_auth():
    """Testar especificamente a autenticação do usuário aluno"""
    try:
        # Conectar ao banco
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        print("🔍 Testando autenticação do usuário aluno...")
        
        # Testar com diferentes senhas
        senhas_teste = ['aluno123', 'aluno', '123', 'password', 'admin123']
        
        for senha in senhas_teste:
            print(f"\n🔐 Testando senha: '{senha}'")
            
            try:
                user = User.authenticate('aluno', senha, db)
                if user:
                    print(f"  ✅ SUCESSO! Usuário autenticado: {user.username}")
                    print(f"  📝 Nome: {user.first_name} {user.last_name}")
                    print(f"  🏷️ Tipo: {user.user_type}")
                    print(f"  🔑 É admin? {user.is_admin}")
                    print(f"  👨‍🏫 É professor? {user.is_professor}")
                    print(f"  👨‍🎓 É aluno? {user.is_aluno}")
                    break
                else:
                    print(f"  ❌ Falha na autenticação")
            except Exception as e:
                print(f"  ❌ Erro na autenticação: {e}")
        
        # Verificar se o usuário existe diretamente
        print(f"\n🔍 Verificando usuário diretamente no banco...")
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE username = 'aluno'")
        aluno_db = cur.fetchone()
        
        if aluno_db:
            print(f"  ✅ Usuário encontrado no banco:")
            print(f"    ID: {aluno_db['id']}")
            print(f"    Username: {aluno_db['username']}")
            print(f"    Senha hash: {aluno_db['password_hash'][:50]}...")
            
            # Verificar se a senha 'aluno123' está correta
            from werkzeug.security import check_password_hash
            senha_correta = check_password_hash(aluno_db['password_hash'], 'aluno123')
            print(f"    Senha 'aluno123' está correta? {senha_correta}")
            
            # Verificar outras senhas
            for senha in ['aluno', '123', 'password']:
                esta_correta = check_password_hash(aluno_db['password_hash'], senha)
                print(f"    Senha '{senha}' está correta? {esta_correta}")
        else:
            print("  ❌ Usuário não encontrado no banco")
        
        cur.close()
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    test_aluno_auth()
