#!/usr/bin/env python3
"""
Teste simples de conexão com PostgreSQL
"""

import psycopg2
import os

def test_connection():
    """Testar conexão simples com PostgreSQL"""
    try:
        print("🔌 Testando conexão simples com PostgreSQL...")
        print(f"📁 Diretório atual: {os.getcwd()}")
        print(f"🐍 Versão do Python: {os.sys.version}")
        
        # Verificar variáveis de ambiente
        print(f"🏠 HOST: {os.getenv('PGHOST', 'localhost')}")
        print(f"🔌 PORT: {os.getenv('PGPORT', '5432')}")
        print(f"👤 USER: {os.getenv('PGUSER', 'postgres')}")
        print(f"🗄️  DATABASE: {os.getenv('PGDATABASE', 'postgres')}")
        
        # Conectar ao banco postgres (padrão)
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="postgres"
        )
        
        print("✅ Conexão bem-sucedida!")
        
        # Testar uma query simples
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()
        print(f"📊 Versão do PostgreSQL: {version[0]}")
        
        cur.close()
        conn.close()
        
        print("🎉 Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print(f"🔍 Tipo do erro: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_connection()
