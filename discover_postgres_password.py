#!/usr/bin/env python3
"""
Descobrir senha do PostgreSQL local
"""
import psycopg
from psycopg.rows import dict_row

def discover_postgres_password():
    """Descobre a senha do PostgreSQL testando senhas comuns"""
    print("🔍 Descobrindo senha do PostgreSQL local...")
    
    # Senhas comuns para testar
    common_passwords = [
        '',  # Sem senha
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
        'localhost'
    ]
    
    for password in common_passwords:
        print(f"\n🔐 Testando senha: '{password if password else '(vazia)'}'")
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
            
            print(f"✅ SUCESSO! Senha encontrada: '{password if password else '(vazia)'}'")
            
            # Testar se pode criar usuário
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
                print(f"   ❌ Erro: {str(e)[:100]}...")
    
    print("\n❌ Nenhuma senha funcionou!")
    print("\n💡 Possíveis soluções:")
    print("   1. Verificar se PostgreSQL está rodando")
    print("   2. Verificar se usuário postgres existe")
    print("   3. Redefinir senha do PostgreSQL")
    print("   4. Reinstalar PostgreSQL")
    
    return None

if __name__ == '__main__':
    discover_postgres_password()

