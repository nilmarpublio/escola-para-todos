#!/usr/bin/env python3
"""
Descoberta inteligente de senha do PostgreSQL
"""
import psycopg
from psycopg.rows import dict_row
import subprocess
import os

def try_psql_connection():
    """Tenta conectar via psql para descobrir a senha"""
    print("🔍 Tentando descobrir senha via psql...")
    
    psql_path = r"C:\Program Files\PostgreSQL\17\bin\psql.exe"
    
    # Teste 1: psql sem senha
    print("\n1️⃣ Tentando psql sem senha...")
    try:
        result = subprocess.run([
            psql_path, 
            "-U", "postgres", 
            "-d", "postgres", 
            "-c", "SELECT current_user, current_database();"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ psql sem senha - SUCESSO!")
            print(f"   Saída: {result.stdout.strip()}")
            return None  # Sem senha
        else:
            print(f"❌ Falhou: {result.stderr.strip()}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 2: psql com senha postgres
    print("\n2️⃣ Tentando psql com senha 'postgres'...")
    try:
        # Criar arquivo temporário com senha
        with open('pgpass.txt', 'w') as f:
            f.write('localhost:5432:postgres:postgres:postgres\n')
        
        # Definir variável de ambiente
        env = os.environ.copy()
        env['PGPASSFILE'] = 'pgpass.txt'
        
        result = subprocess.run([
            psql_path, 
            "-U", "postgres", 
            "-d", "postgres", 
            "-c", "SELECT current_user, current_database();"
        ], capture_output=True, text=True, timeout=10, env=env)
        
        if result.returncode == 0:
            print("✅ psql com senha 'postgres' - SUCESSO!")
            print(f"   Saída: {result.stdout.strip()}")
            os.remove('pgpass.txt')
            return 'postgres'
        else:
            print(f"❌ Falhou: {result.stderr.strip()}")
            
        os.remove('pgpass.txt')
    except Exception as e:
        print(f"❌ Erro: {e}")
        if os.path.exists('pgpass.txt'):
            os.remove('pgpass.txt')
    
    return None

def test_common_passwords_with_psycopg():
    """Testa senhas comuns com psycopg"""
    print("\n🔍 Testando senhas comuns com psycopg...")
    
    # Senhas mais específicas para PostgreSQL
    passwords = [
        'postgres',
        'admin',
        'password',
        '123456',
        'root',
        'user',
        'test',
        '1234',
        'admin123',
        'postgresql',
        'dbadmin',
        'database',
        'server',
        'localhost',
        'nilma',  # Seu usuário Windows
        'windows',
        'user123',
        'pass123',
        'sql123',
        'db123'
    ]
    
    for password in passwords:
        print(f"\n🔐 Testando: '{password}'")
        try:
            conn = psycopg.connect(
                host='localhost',
                port=5432,
                dbname='postgres',
                user='postgres',
                password=password,
                row_factory=dict_row,
                connect_timeout=5
            )
            
            print(f"✅ SUCESSO! Senha: '{password}'")
            
            cur = conn.cursor()
            cur.execute("SELECT current_user, current_database(), version();")
            result = cur.fetchone()
            print(f"   👤 Usuário: {result['current_user']}")
            print(f"   🗄️ Banco: {result['current_database']}")
            print(f"   📊 Versão: {result['version'].split(',')[0]}")
            
            cur.close()
            conn.close()
            return password
            
        except Exception as e:
            if "autenticação do tipo senha falhou" in str(e):
                print("   ❌ Senha incorreta")
            elif "no password supplied" in str(e):
                print("   ❌ Senha necessária")
            else:
                print(f"   ❌ Erro: {str(e)[:80]}...")
    
    return None

def main():
    """Função principal"""
    print("🚀 Descoberta inteligente de senha PostgreSQL")
    print("=" * 50)
    
    # Tentar via psql primeiro
    password = try_psql_connection()
    if password is not None or password == '':  # None = sem senha, '' = sem senha
        print(f"\n🎉 Senha descoberta via psql: '{password if password else '(vazia)'}'")
        return password
    
    # Tentar via psycopg
    password = test_common_passwords_with_psycopg()
    if password:
        print(f"\n🎉 Senha descoberta via psycopg: '{password}'")
        return password
    
    print("\n❌ Nenhuma senha foi descoberta!")
    print("\n💡 Soluções:")
    print("   1. Verificar se você anotou a senha durante a instalação")
    print("   2. Redefinir senha via pgAdmin")
    print("   3. Reinstalar PostgreSQL")
    print("   4. Verificar arquivo de configuração pg_hba.conf")
    
    return None

if __name__ == '__main__':
    main()

