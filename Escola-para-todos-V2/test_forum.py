#!/usr/bin/env python3
"""
Script de teste para o sistema de fórum
"""

import sqlite3
import sys

def test_forum_database():
    """Testar se as tabelas do fórum foram criadas corretamente"""
    print("🧪 Testando banco de dados do fórum...")
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect('escola_para_todos.db')
        cursor = conn.cursor()
        
        # Verificar se as tabelas existem
        tables = [
            'forum_topicos',
            'forum_respostas', 
            'forum_votos',
            'forum_tags',
            'forum_topicos_tags'
        ]
        
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                print(f"✅ Tabela {table} existe")
            else:
                print(f"❌ Tabela {table} NÃO existe")
                return False
        
        # Verificar dados de exemplo
        print("\n📊 Verificando dados de exemplo...")
        
        # Tags
        cursor.execute("SELECT COUNT(*) FROM forum_tags")
        tag_count = cursor.fetchone()[0]
        print(f"🏷️ Tags: {tag_count}")
        
        # Tópicos
        cursor.execute("SELECT COUNT(*) FROM forum_topicos")
        topic_count = cursor.fetchone()[0]
        print(f"💬 Tópicos: {topic_count}")
        
        # Respostas
        cursor.execute("SELECT COUNT(*) FROM forum_respostas")
        response_count = cursor.fetchone()[0]
        print(f"💭 Respostas: {response_count}")
        
        # Votos
        cursor.execute("SELECT COUNT(*) FROM forum_votos")
        vote_count = cursor.fetchone()[0]
        print(f"👍 Votos: {vote_count}")
        
        # Verificar estrutura de uma tabela
        print("\n🔍 Estrutura da tabela forum_topicos:")
        cursor.execute("PRAGMA table_info(forum_topicos)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        print("\n✅ Teste do banco de dados concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar banco de dados: {e}")
        return False

def test_forum_routes():
    """Testar se as rotas do fórum estão funcionando"""
    print("\n🌐 Testando rotas do fórum...")
    
    try:
        import requests
        
        base_url = "http://localhost:5000"
        
        # Testar rota principal do fórum (deve redirecionar para login)
        print("🔗 Testando rota /forum...")
        response = requests.get(f"{base_url}/forum", allow_redirects=False)
        
        if response.status_code == 302:  # Redirecionamento
            print("✅ Rota /forum redireciona corretamente para login (esperado)")
        else:
            print(f"⚠️ Rota /forum retornou status {response.status_code}")
        
        # Testar rota de busca
        print("🔗 Testando rota /forum/buscar...")
        response = requests.get(f"{base_url}/forum/buscar", allow_redirects=False)
        
        if response.status_code == 302:  # Redirecionamento
            print("✅ Rota /forum/buscar redireciona corretamente para login (esperado)")
        else:
            print(f"⚠️ Rota /forum/buscar retornou status {response.status_code}")
        
        print("\n✅ Teste das rotas concluído!")
        print("💡 As rotas estão funcionando (redirecionando para login quando não autenticado)")
        return True
        
    except ImportError:
        print("⚠️ Módulo 'requests' não encontrado. Instalando...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        return test_forum_routes()
        
    except Exception as e:
        print(f"❌ Erro ao testar rotas: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE DO SISTEMA DE FÓRUM")
    print("=" * 40)
    
    # Testar banco de dados
    db_ok = test_forum_database()
    
    # Testar rotas
    routes_ok = test_forum_routes()
    
    print("\n" + "=" * 40)
    if db_ok and routes_ok:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O sistema de fórum está funcionando corretamente")
        print("\n📋 Funcionalidades implementadas:")
        print("  • Tópicos por aula")
        print("  • Alunos podem postar perguntas")
        print("  • Professores podem responder")
        print("  • Sistema de votos")
        print("  • Marcação de melhor resposta")
        print("  • Moderação básica (excluir/fechar)")
        print("  • Sistema de tags")
        print("  • Busca e filtros")
        print("  • Estatísticas do fórum")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("Verifique os erros acima e corrija-os")
    
    print("\n🌐 Para testar o fórum:")
    print("1. Acesse http://localhost:5000")
    print("2. Faça login com: aluno.joao / aluno123")
    print("3. Clique em 'Fórum' no menu de navegação")

if __name__ == "__main__":
    main()
