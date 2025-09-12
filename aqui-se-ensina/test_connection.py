#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import sys

def test_connection():
    """Testar conexão com PostgreSQL"""
    try:
        print("Tentando conectar ao PostgreSQL...")
        
        # Tentar diferentes formatos de conexão
        connection_strings = [
            "postgresql://postgres:postgres@localhost:5432/postgres",
            "host=localhost port=5432 dbname=postgres user=postgres password=postgres",
            "postgresql://postgres:postgres@localhost:5432/postgres?client_encoding=utf8"
        ]
        
        for i, conn_str in enumerate(connection_strings):
            print(f"\nTentativa {i+1}: {conn_str}")
            try:
                if conn_str.startswith("postgresql://"):
                    conn = psycopg2.connect(conn_str)
                else:
                    conn = psycopg2.connect(conn_str)
                
                print("✅ Conexão bem-sucedida!")
                cur = conn.cursor()
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print(f"Versão do PostgreSQL: {version[0]}")
                cur.close()
                conn.close()
                return True
                
            except Exception as e:
                print(f"❌ Falha na tentativa {i+1}: {type(e).__name__}: {e}")
                continue
        
        return False
        
    except Exception as e:
        print(f"Erro geral: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n🎉 Teste de conexão bem-sucedido!")
    else:
        print("\n💥 Todas as tentativas de conexão falharam!")
        sys.exit(1)
