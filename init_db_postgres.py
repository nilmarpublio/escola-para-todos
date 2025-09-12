#!/usr/bin/env python3
"""
Script para inicializar o banco de dados PostgreSQL no Render
"""

import os
import psycopg
from psycopg.rows import dict_row
from werkzeug.security import generate_password_hash
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_db_connection():
    """Conectar ao banco PostgreSQL"""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Render usa DATABASE_URL
        try:
            # Tentar conectar diretamente
            return psycopg.connect(database_url, row_factory=dict_row)
        except Exception as e:
            print(f"❌ Erro ao conectar com DATABASE_URL: {e}")
            print(f"📋 DATABASE_URL: {database_url}")
            
            # Tentar parsear a URL manualmente
            try:
                from urllib.parse import urlparse
                parsed = urlparse(database_url)
                
                # Extrair componentes
                host = parsed.hostname
                port = parsed.port or 5432
                dbname = parsed.path[1:]  # Remove a barra inicial
                username = parsed.username
                password = parsed.password
                
                print(f"🔍 Componentes extraídos:")
                print(f"   Host: {host}")
                print(f"   Port: {port}")
                print(f"   Database: {dbname}")
                print(f"   Username: {username}")
                print(f"   Password: {'*' * len(password) if password else 'None'}")
                
                # Conectar com componentes separados
                return psycopg.connect(
                    host=host,
                    port=port,
                    dbname=dbname,
                    user=username,
                    password=password,
                    row_factory=dict_row
                )
            except Exception as e2:
                print(f"❌ Erro ao parsear URL manualmente: {e2}")
                raise e
    else:
        # Configuração local
        return psycopg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            dbname=os.getenv('DB_NAME', 'escola_para_todos'),
            user=os.getenv('DB_USER', 'escola_user'),
            password=os.getenv('DB_PASSWORD', ''),
            row_factory=dict_row
        )

def create_tables(db):
    """Criar tabelas do banco de dados"""
    cur = db.cursor()
    
    # Tabela de usuários
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            user_type VARCHAR(20) NOT NULL DEFAULT 'aluno',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de turmas
    cur.execute('''
        CREATE TABLE IF NOT EXISTS turmas (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            descricao TEXT,
            professor_id INTEGER REFERENCES users(id),
            max_alunos INTEGER DEFAULT 30,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de aulas
    cur.execute('''
        CREATE TABLE IF NOT EXISTS aulas (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(200) NOT NULL,
            conteudo TEXT NOT NULL,
            turma_id INTEGER REFERENCES turmas(id),
            ordem INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de matrículas
    cur.execute('''
        CREATE TABLE IF NOT EXISTS matriculas (
            id SERIAL PRIMARY KEY,
            aluno_id INTEGER REFERENCES users(id),
            turma_id INTEGER REFERENCES turmas(id),
            data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'ativa',
            UNIQUE(aluno_id, turma_id)
        )
    ''')
    
    # Tabela de progresso
    cur.execute('''
        CREATE TABLE IF NOT EXISTS progresso (
            id SERIAL PRIMARY KEY,
            aluno_id INTEGER REFERENCES users(id),
            aula_id INTEGER REFERENCES aulas(id),
            status VARCHAR(20) DEFAULT 'não iniciada',
            data_inicio TIMESTAMP,
            data_conclusao TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de exercícios
    cur.execute('''
        CREATE TABLE IF NOT EXISTS exercicios (
            id SERIAL PRIMARY KEY,
            aula_id INTEGER REFERENCES aulas(id),
            pergunta TEXT NOT NULL,
            tipo VARCHAR(20) DEFAULT 'multipla_escolha',
            opcoes JSONB,
            resposta_correta TEXT,
            pontos INTEGER DEFAULT 10,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de respostas dos exercícios
    cur.execute('''
        CREATE TABLE IF NOT EXISTS respostas_exercicios (
            id SERIAL PRIMARY KEY,
            aluno_id INTEGER REFERENCES users(id),
            exercicio_id INTEGER REFERENCES exercicios(id),
            resposta TEXT,
            esta_correta BOOLEAN,
            pontos_ganhos INTEGER DEFAULT 0,
            data_resposta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de fórum
    cur.execute('''
        CREATE TABLE IF NOT EXISTS forum_topicos (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(200) NOT NULL,
            conteudo TEXT NOT NULL,
            autor_id INTEGER REFERENCES users(id),
            aula_id INTEGER REFERENCES aulas(id),
            tipo VARCHAR(20) DEFAULT 'duvida',
            status VARCHAR(20) DEFAULT 'aberto',
            visualizacoes INTEGER DEFAULT 0,
            ativo BOOLEAN DEFAULT TRUE,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de respostas do fórum
    cur.execute('''
        CREATE TABLE IF NOT EXISTS forum_respostas (
            id SERIAL PRIMARY KEY,
            topico_id INTEGER REFERENCES forum_topicos(id),
            autor_id INTEGER REFERENCES users(id),
            conteudo TEXT NOT NULL,
            ativo BOOLEAN DEFAULT TRUE,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de tags do fórum
    cur.execute('''
        CREATE TABLE IF NOT EXISTS forum_tags (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(50) UNIQUE NOT NULL,
            cor VARCHAR(7) DEFAULT '#007bff',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de relacionamento tags-tópicos
    cur.execute('''
        CREATE TABLE IF NOT EXISTS forum_topicos_tags (
            topico_id INTEGER REFERENCES forum_topicos(id),
            tag_id INTEGER REFERENCES forum_tags(id),
            PRIMARY KEY (topico_id, tag_id)
        )
    ''')
    
    # Tabela de conquistas
    cur.execute('''
        CREATE TABLE IF NOT EXISTS conquistas (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            descricao TEXT,
            icone VARCHAR(100),
            pontos_necessarios INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de conquistas dos usuários
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuario_conquistas (
            usuario_id INTEGER REFERENCES users(id),
            conquista_id INTEGER REFERENCES conquistas(id),
            data_conquista TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (usuario_id, conquista_id)
        )
    ''')
    
    # Tabela de pontos dos usuários
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuario_pontos (
            usuario_id INTEGER REFERENCES users(id) PRIMARY KEY,
            pontos_totais INTEGER DEFAULT 0,
            nivel INTEGER DEFAULT 1,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    db.commit()
    cur.close()
    print("✅ Tabelas criadas com sucesso!")

def insert_initial_data(db):
    """Inserir dados iniciais"""
    cur = db.cursor()
    
    # Verificar se já existe usuário admin
    cur.execute('SELECT COUNT(*) as count FROM users WHERE user_type = %s', ('admin',))
    admin_count = cur.fetchone()['count']
    
    if admin_count == 0:
        # Criar usuário administrador
        admin_password = generate_password_hash('admin123')
        now = datetime.utcnow()
        
        cur.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, user_type, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', ('admin', 'admin@educa-facil.com', admin_password, 'Administrador', 'Sistema', 'admin', True, now, now))
        
        admin_id = cur.fetchone()['id']
        
        # Inserir conquistas básicas
        conquistas = [
            ('Primeiro Login', 'Realizou o primeiro login na plataforma', '🎯', 0),
            ('Aluno Dedicado', 'Completou 5 aulas', '📚', 50),
            ('Professor Ativo', 'Criou 3 aulas', '👨‍🏫', 100),
            ('Colaborador', 'Participou do fórum 10 vezes', '💬', 75),
            ('Mestre', 'Alcançou 1000 pontos', '👑', 1000)
        ]
        
        for nome, descricao, icone, pontos in conquistas:
            cur.execute('''
                INSERT INTO conquistas (nome, descricao, icone, pontos_necessarios)
                VALUES (%s, %s, %s, %s)
            ''', (nome, descricao, icone, pontos))
        
        # Inserir pontos iniciais para o admin
        cur.execute('''
            INSERT INTO usuario_pontos (usuario_id, pontos_totais, nivel)
            VALUES (%s, %s, %s)
        ''', (admin_id, 0, 1))
        
        print("✅ Usuário administrador criado!")
        print("   Username: admin")
        print("   Senha: admin123")
        print("   Email: admin@educa-facil.com")
    
    # Inserir tags básicas do fórum
    tags = [
        ('Dúvida', '#007bff'),
        ('Sugestão', '#28a745'),
        ('Bug', '#dc3545'),
        ('Recurso', '#ffc107'),
        ('Geral', '#6c757d')
    ]
    
    for nome, cor in tags:
        cur.execute('''
            INSERT INTO forum_tags (nome, cor)
            VALUES (%s, %s)
            ON CONFLICT (nome) DO NOTHING
        ''', (nome, cor))
    
    db.commit()
    cur.close()
    print("✅ Dados iniciais inseridos com sucesso!")

def main():
    """Função principal"""
    print("🚀 Inicializando banco de dados PostgreSQL...")
    
    try:
        # Conectar ao banco
        db = get_db_connection()
        print("✅ Conectado ao banco PostgreSQL!")
        
        # Criar tabelas
        create_tables(db)
        
        # Inserir dados iniciais
        insert_initial_data(db)
        
        print("🎉 Banco de dados inicializado com sucesso!")
        print("📊 Aplicação pronta para uso!")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False
    
    finally:
        if 'db' in locals():
            db.close()
    
    return True

if __name__ == '__main__':
    main()
