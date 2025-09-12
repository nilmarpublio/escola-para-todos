#!/usr/bin/env python3
"""
Teste de conexao com PostgreSQL usando psycopg3
"""

import psycopg
import os

def test_connection():
    """Testar conexao com PostgreSQL"""
    # Tentar com o usuário do sistema atual
    usuario_atual = os.getenv('USERNAME', 'postgres')
    
    print(f"Usuario atual do sistema: {usuario_atual}")
    
    try:
        print("Tentando conectar com usuario do sistema...")
        
        conn = psycopg.connect(
            host="localhost",
            port=5432,
            dbname="postgres",
            user=usuario_atual
        )
        
        print("Conexao bem-sucedida!")
        
        # Testar uma query simples
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()
        print(f"Versao do PostgreSQL: {version[0]}")
        
        cur.close()
        conn.close()
        
        print("Teste concluido com sucesso!")
        return True
        
    except Exception as e:
        print(f"Falhou com usuario '{usuario_atual}': {e}")
        
        # Tentar com postgres e senha vazia
        try:
            print("Tentando conectar como postgres sem senha...")
            
            conn = psycopg.connect(
                host="localhost",
                port=5432,
                dbname="postgres",
                user="postgres",
                password=""
            )
            
            print("Conexao bem-sucedida!")
            
            # Testar uma query simples
            cur = conn.cursor()
            cur.execute("SELECT version()")
            version = cur.fetchone()
            print(f"Versao do PostgreSQL: {version[0]}")
            
            cur.close()
            conn.close()
            
            print("Teste concluido com sucesso!")
            return True
            
        except Exception as e2:
            print(f"Falhou com postgres sem senha: {e2}")
    
    print("Todas as tentativas falharam!")
    return False

if __name__ == "__main__":
    test_connection()
