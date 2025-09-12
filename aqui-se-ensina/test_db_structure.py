#!/usr/bin/env python3
"""
Script para testar a estrutura da tabela aulas e identificar problemas
"""

import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_database_structure():
    """Testa a estrutura da tabela aulas"""
    try:
        # Conectar ao banco
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            # Render usa DATABASE_URL
            db = psycopg.connect(database_url, row_factory=dict_row)
        else:
            # Configuração local
            db = psycopg.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                dbname=os.getenv('DB_NAME', 'escola_para_todos'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres'),
                row_factory=dict_row
            )
        
        print("✅ Conexão com banco estabelecida")
        
        cur = db.cursor()
        
        # 1. Verificar se a tabela aulas existe
        print("\n🔍 1. Verificando se a tabela 'aulas' existe...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'aulas'
            )
        """)
        table_exists = cur.fetchone()['exists']
        print(f"   Tabela 'aulas' existe: {table_exists}")
        
        if not table_exists:
            print("❌ Tabela 'aulas' não existe!")
            return
        
        # 2. Verificar estrutura da tabela aulas
        print("\n🔍 2. Verificando estrutura da tabela 'aulas'...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'aulas'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("   Colunas encontradas:")
        for col in columns:
            print(f"   - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # 3. Verificar se há dados na tabela
        print("\n🔍 3. Verificando se há dados na tabela...")
        cur.execute("SELECT COUNT(*) as total FROM aulas")
        total_aulas = cur.fetchone()['total']
        print(f"   Total de aulas: {total_aulas}")
        
        if total_aulas > 0:
            # 4. Verificar valores únicos na coluna serie
            print("\n🔍 4. Verificando valores únicos na coluna 'serie'...")
            cur.execute("SELECT DISTINCT serie FROM aulas ORDER BY serie")
            series = cur.fetchall()
            print("   Séries encontradas:")
            for serie in series:
                print(f"   - {serie['serie']}")
            
            # 5. Verificar algumas aulas de exemplo
            print("\n🔍 5. Verificando algumas aulas de exemplo...")
            cur.execute("""
                SELECT id, titulo, serie, 
                       COALESCE(duracao_minutos, duracao, 'N/A') as duracao
                FROM aulas 
                LIMIT 5
            """)
            
            aulas_exemplo = cur.fetchall()
            print("   Aulas de exemplo:")
            for aula in aulas_exemplo:
                print(f"   - ID {aula['id']}: {aula['titulo']} (Série: {aula['serie']}, Duração: {aula['duracao']})")
        
        # 6. Testar as queries específicas que estão falhando
        print("\n🔍 6. Testando queries específicas...")
        
        # Query para educação infantil
        print("   Testando query para educação infantil...")
        try:
            cur.execute("""
                SELECT COUNT(*) as total
                FROM aulas 
                WHERE serie IN ('infantil', 'pre-escola') AND is_active = true
            """)
            count_infantil = cur.fetchone()['total']
            print(f"   ✅ Aulas infantis: {count_infantil}")
        except Exception as e:
            print(f"   ❌ Erro na query infantil: {e}")
        
        # Query para anos iniciais
        print("   Testando query para anos iniciais...")
        try:
            cur.execute("""
                SELECT COUNT(*) as total
                FROM aulas 
                WHERE serie IN ('1ano', '2ano', '3ano', '4ano', '5ano') AND is_active = true
            """)
            count_iniciais = cur.fetchone()['total']
            print(f"   ✅ Aulas anos iniciais: {count_iniciais}")
        except Exception as e:
            print(f"   ❌ Erro na query anos iniciais: {e}")
        
        # Query para anos finais
        print("   Testando query para anos finais...")
        try:
            cur.execute("""
                SELECT COUNT(*) as total
                FROM aulas 
                WHERE serie IN ('6ano', '7ano', '8ano', '9ano') AND is_active = true
            """)
            count_finais = cur.fetchone()['total']
            print(f"   ✅ Aulas anos finais: {count_finais}")
        except Exception as e:
            print(f"   ❌ Erro na query anos finais: {e}")
        
        cur.close()
        db.close()
        
        print("\n✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_structure()

