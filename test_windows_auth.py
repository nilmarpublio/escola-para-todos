#!/usr/bin/env python3
"""
Teste de autenticação Windows com PostgreSQL
"""
import psycopg
from psycopg.rows import dict_row
import os

def test_windows_auth():
    """Testa autenticação Windows"""
    print("🔍 Testando autenticação Windows com PostgreSQL...")
    
    # Obter usuário atual do Windows
    current_user = os.getenv('USERNAME', os.getenv('USER', 'unknown'))
    print(f"👤 Usuário Windows atual: {current_user}")
    
    # Teste 1: Conexão sem especificar usuário (usa usuário Windows)
    print("\n1️⃣ Tentando conexão sem especificar usuário...")
    try:
        conn = psycopg.connect(
            host='localhost',
            port=5432,
            dbname='postgres',
            row_factory=dict_row,
            connect_timeout=5
        )
        print("✅ Conexão sem usuário - SUCESSO!")
        
        cur = conn.cursor()
        cur.execute("SELECT current_user, current_database();")
        result = cur.fetchone()
        print(f"   👤 Usuário conectado: {result['current_user']}")
        print(f"   🗄️ Banco: {result['current_database']}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Falhou: {str(e)[:100]}...")
    
    # Teste 2: Conexão com usuário Windows
    print(f"\n2️⃣ Tentando conexão com usuário Windows: {current_user}")
    try:
        conn = psycopg.connect(
            host='localhost',
            port=5432,
            dbname='postgres',
            user=current_user,
            row_factory=dict_row,
            connect_timeout=5
        )
        print("✅ Conexão com usuário Windows - SUCESSO!")
        
        cur = conn.cursor()
        cur.execute("SELECT current_user, current_database();")
        result = cur.fetchone()
        print(f"   👤 Usuário conectado: {result['current_user']}")
        print(f"   🗄️ Banco: {result['current_database']}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Falhou: {str(e)[:100]}...")
    
    # Teste 3: Conexão com usuário postgres e senha vazia (trust auth)
    print("\n3️⃣ Tentando conexão com usuário postgres e senha vazia...")
    try:
        conn = psycopg.connect(
            host='localhost',
            port=5432,
            dbname='postgres',
            user='postgres',
            password='',
            row_factory=dict_row,
            connect_timeout=5
        )
        print("✅ Conexão postgres sem senha - SUCESSO!")
        
        cur = conn.cursor()
        cur.execute("SELECT current_user, current_database();")
        result = cur.fetchone()
        print(f"   👤 Usuário conectado: {result['current_user']}")
        print(f"   🗄️ Banco: {result['current_database']}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Falhou: {str(e)[:100]}...")
    
    print("\n❌ Nenhuma autenticação funcionou!")
    return False

if __name__ == '__main__':
    test_windows_auth()

