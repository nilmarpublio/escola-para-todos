#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar e listar todas as mensagens de erro do aplicativo
"""

import sqlite3
import os
import sys

def check_database_tables():
    """Verificar se todas as tabelas necessárias existem"""
    print("=" * 60)
    print("1. VERIFICAÇÃO DAS TABELAS DO BANCO DE DADOS")
    print("=" * 60)
    
    try:
        db = sqlite3.connect('escola_para_todos.db')
        cursor = db.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Tabelas encontradas ({len(tables)}):")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table[0]}")
        
        # Verificar tabelas específicas necessárias para gamificação
        required_tables = [
            'niveis_aluno',
            'metas_semanais', 
            'progresso_metas',
            'aluno_conquista',
            'conquistas',
            'historico_pontos'
        ]
        
        print(f"\nTabelas necessárias para gamificação:")
        for i, table_name in enumerate(required_tables, 1):
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {i}. {table_name}: {count} registros")
            
        cursor.close()
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")

def check_sample_data():
    """Verificar se há dados de exemplo nas tabelas"""
    print("\n" + "=" * 60)
    print("2. VERIFICAÇÃO DE DADOS DE EXEMPLO")
    print("=" * 60)
    
    try:
        db = sqlite3.connect('escola_para_todos.db')
        cursor = db.cursor()
        
        # Verificar usuários
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"1. Usuários: {user_count}")
        
        # Verificar turmas
        cursor.execute("SELECT COUNT(*) FROM turmas")
        turma_count = cursor.fetchone()[0]
        print(f"2. Turmas: {turma_count}")
        
        # Verificar aulas
        cursor.execute("SELECT COUNT(*) FROM aulas")
        aula_count = cursor.fetchone()[0]
        print(f"3. Aulas: {aula_count}")
        
        # Verificar níveis de alunos
        cursor.execute("SELECT COUNT(*) FROM niveis_aluno")
        nivel_count = cursor.fetchone()[0]
        print(f"4. Níveis de alunos: {nivel_count}")
        
        # Verificar metas
        cursor.execute("SELECT COUNT(*) FROM metas_semanais")
        meta_count = cursor.fetchone()[0]
        print(f"5. Metas semanais: {meta_count}")
        
        cursor.close()
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")

def check_sql_queries():
    """Verificar se as consultas SQL estão funcionando"""
    print("\n" + "=" * 60)
    print("3. VERIFICAÇÃO DAS CONSULTAS SQL")
    print("=" * 60)
    
    try:
        db = sqlite3.connect('escola_para_todos.db')
        cursor = db.cursor()
        
        # Testar consulta de níveis
        print("1. Testando consulta de níveis...")
        cursor.execute("""
            SELECT nivel_atual, pontos_totais, pontos_nivel_atual, pontos_proximo_nivel, 
                   titulo_nivel, cor_nivel, icone_nivel
            FROM niveis_aluno 
            LIMIT 1
        """)
        nivel_result = cursor.fetchone()
        print(f"   Resultado: {nivel_result}")
        print(f"   Tipo: {type(nivel_result)}")
        
        # Testar consulta de metas
        print("\n2. Testando consulta de metas...")
        cursor.execute("""
            SELECT m.id, m.nome, m.descricao, m.tipo, m.valor_meta, m.pontos_recompensa, 
                   m.recompensa_virtual, m.data_inicio, m.data_fim,
                   COALESCE(pm.valor_atual, 0) as valor_atual,
                   COALESCE(pm.concluida, 0) as concluida,
                   COALESCE(pm.recompensa_coletada, 0) as recompensa_coletada
            FROM metas_semanais m
            LEFT JOIN progresso_metas pm ON m.id = pm.meta_id
            LIMIT 1
        """)
        meta_result = cursor.fetchone()
        print(f"   Resultado: {meta_result}")
        print(f"   Tipo: {type(meta_result)}")
        
        cursor.close()
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao testar consultas: {e}")

def check_file_structure():
    """Verificar estrutura dos arquivos"""
    print("\n" + "=" * 60)
    print("4. VERIFICAÇÃO DA ESTRUTURA DOS ARQUIVOS")
    print("=" * 60)
    
    required_files = [
        'app.py',
        'init_db.py',
        'templates/student_gamificacao.html',
        'escola_para_todos.db'
    ]
    
    for i, file_path in enumerate(required_files, 1):
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"{i}. {file_path}: ✅ Existe ({size} bytes)")
        else:
            print(f"{i}. {file_path}: ❌ Não encontrado")

def check_python_syntax():
    """Verificar sintaxe Python dos arquivos principais"""
    print("\n" + "=" * 60)
    print("5. VERIFICAÇÃO DE SINTAXE PYTHON")
    print("=" * 60)
    
    python_files = ['app.py', 'init_db.py']
    
    for i, file_path in enumerate(python_files, 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Tentar compilar o código
            compile(content, file_path, 'exec')
            print(f"{i}. {file_path}: ✅ Sintaxe válida")
            
        except SyntaxError as e:
            print(f"{i}. {file_path}: ❌ Erro de sintaxe na linha {e.lineno}: {e.msg}")
        except Exception as e:
            print(f"{i}. {file_path}: ❌ Erro ao verificar: {e}")

def main():
    """Função principal"""
    print("🔍 DEBUG COMPLETO DO APLICATIVO ESCOLA PARA TODOS")
    print("=" * 60)
    
    check_database_tables()
    check_sample_data()
    check_sql_queries()
    check_file_structure()
    check_python_syntax()
    
    print("\n" + "=" * 60)
    print("✅ VERIFICAÇÃO COMPLETA FINALIZADA")
    print("=" * 60)
    print("\nSe houver erros, verifique:")
    print("1. Se o banco de dados foi inicializado (python init_db.py)")
    print("2. Se todas as tabelas foram criadas")
    print("3. Se há dados de exemplo")
    print("4. Se a sintaxe Python está correta")

if __name__ == "__main__":
    main()
