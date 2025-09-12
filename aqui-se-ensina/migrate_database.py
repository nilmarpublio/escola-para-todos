#!/usr/bin/env python3
"""
Script para migrar banco de dados local para o Render
"""

import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from datetime import datetime

def export_local_database():
    """Exporta dados do banco local"""
    print("📤 Exportando banco de dados local...")
    
    try:
        # Conectar ao banco local
        conn = psycopg.connect(
            host='localhost',
            port=5432,
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        cur = conn.cursor()
        
        # Listar todas as tabelas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        
        print(f"📋 Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        # Exportar dados de cada tabela
        exported_data = {}
        
        for table in tables:
            table_name = table['table_name']
            print(f"\n📊 Exportando tabela: {table_name}")
            
            try:
                # Obter estrutura da tabela
                cur.execute(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
                
                # Obter dados da tabela
                cur.execute(f"SELECT * FROM {table_name}")
                rows = cur.fetchall()
                
                exported_data[table_name] = {
                    'columns': columns,
                    'data': rows
                }
                
                print(f"   ✅ {len(rows)} registros exportados")
                
            except Exception as e:
                print(f"   ❌ Erro ao exportar {table_name}: {e}")
        
        cur.close()
        conn.close()
        
        # Salvar dados exportados
        import json
        from datetime import datetime
        
        # Converter para formato serializável
        serializable_data = {}
        for table_name, table_data in exported_data.items():
            serializable_data[table_name] = {
                'columns': [dict(col) for col in table_data['columns']],
                'data': []
            }
            
            # Converter cada linha para formato serializável
            for row in table_data['data']:
                serializable_row = {}
                for key, value in row.items():
                    if isinstance(value, datetime):
                        serializable_row[key] = value.isoformat()
                    else:
                        serializable_row[key] = value
                serializable_data[table_name]['data'].append(serializable_row)
        
        # Salvar arquivo de migração
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"database_migration_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Dados exportados para: {filename}")
        print(f"📊 Total de tabelas: {len(exported_data)}")
        
        # Mostrar resumo
        total_records = sum(len(table_data['data']) for table_data in exported_data.values())
        print(f"📊 Total de registros: {total_records}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Erro ao exportar banco: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_migration_sql():
    """Cria script SQL para migração"""
    print("\n📝 Criando script SQL de migração...")
    
    try:
        # Conectar ao banco local
        conn = psycopg.connect(
            host='localhost',
            port=5432,
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        cur = conn.cursor()
        
        # Obter estrutura das tabelas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        
        sql_script = []
        sql_script.append("-- Script de migração para Render")
        sql_script.append("-- Gerado automaticamente")
        sql_script.append("")
        
        for table in tables:
            table_name = table['table_name']
            print(f"   📋 Processando tabela: {table_name}")
            
            # Obter estrutura da tabela
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
            
            # Obter dados da tabela
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            
            if rows:
                # Criar INSERT statements
                column_names = [col['column_name'] for col in columns]
                placeholders = ', '.join(['%s'] * len(column_names))
                
                sql_script.append(f"-- Tabela: {table_name}")
                sql_script.append(f"-- {len(rows)} registros")
                sql_script.append("")
                
                for row in rows:
                    values = []
                    for col in columns:
                        col_name = col['column_name']
                        value = row[col_name]
                        
                        if value is None:
                            values.append('NULL')
                        elif isinstance(value, str):
                            # Escapar aspas simples
                            escaped_value = value.replace("'", "''")
                            values.append(f"'{escaped_value}'")
                        elif isinstance(value, bool):
                            values.append('true' if value else 'false')
                        else:
                            values.append(str(value))
                    
                    values_str = ', '.join(values)
                    sql_script.append(f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({values_str});")
                
                sql_script.append("")
        
        cur.close()
        conn.close()
        
        # Salvar script SQL
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sql_filename = f"migration_script_{timestamp}.sql"
        
        with open(sql_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_script))
        
        print(f"💾 Script SQL criado: {sql_filename}")
        return sql_filename
        
    except Exception as e:
        print(f"❌ Erro ao criar script SQL: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 Iniciando migração do banco de dados...")
    print("=" * 50)
    
    # Exportar dados
    export_file = export_local_database()
    
    if export_file:
        print("\n" + "=" * 50)
        # Criar script SQL
        sql_file = create_migration_sql()
        
        if sql_file:
            print(f"\n🎉 Migração concluída com sucesso!")
            print(f"📁 Arquivos gerados:")
            print(f"   - {export_file} (dados em JSON)")
            print(f"   - {sql_file} (script SQL)")
            print(f"\n💡 Para usar no Render:")
            print(f"   1. Copie o arquivo {sql_file}")
            print(f"   2. Execute no banco do Render via psql ou console")
            print(f"   3. Ou use o arquivo JSON para migração programática")
        else:
            print("❌ Falha ao criar script SQL")
    else:
        print("❌ Falha ao exportar banco")
