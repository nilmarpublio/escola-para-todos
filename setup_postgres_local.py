#!/usr/bin/env python3
"""
Script para configurar o banco de dados PostgreSQL local
"""

import psycopg
from psycopg.rows import dict_row
from werkzeug.security import generate_password_hash
from datetime import datetime

def get_db_connection():
    """Conectar ao banco PostgreSQL local"""
    return psycopg.connect(
        host='localhost',
        dbname='postgres',  # Conectar ao banco padrão primeiro
        user='postgres',
        password='postgres',
        row_factory=dict_row
    )

def setup_database():
    """Configurar banco de dados e usuário"""
    try:
        # Conectar como postgres (usuário administrador)
        db = get_db_connection()
        cur = db.cursor()
        
        print("🔧 Configurando banco de dados PostgreSQL...")
        
        # Criar banco de dados escola_para_todos se não existir
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'escola_para_todos'")
        if not cur.fetchone():
            print("📁 Criando banco de dados 'escola_para_todos'...")
            # Fechar conexão atual para criar o banco
            cur.close()
            db.close()
            
            # Criar banco sem transação
            db = psycopg.connect(
                host='localhost',
                dbname='postgres',
                user='postgres',
                password='postgres',
                autocommit=True  # Importante para CREATE DATABASE
            )
            cur = db.cursor()
            cur.execute("CREATE DATABASE escola_para_todos")
            cur.close()
            db.close()
            print("✅ Banco de dados criado com sucesso!")
            
            # Reconectar para continuar
            db = psycopg.connect(
                host='localhost',
                dbname='postgres',
                user='postgres',
                password='postgres',
                row_factory=dict_row
            )
            cur = db.cursor()
        else:
            print("ℹ️ Banco de dados 'escola_para_todos' já existe")
        
        # Fechar conexão com postgres
        cur.close()
        db.close()
        
        # Conectar ao banco escola_para_todos
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        cur = db.cursor()
        
        print("🔧 Criando tabelas...")
        
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
        
        # Tabela de aulas
        cur.execute('''
            CREATE TABLE IF NOT EXISTS aulas (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(200) NOT NULL,
                descricao TEXT,
                conteudo TEXT NOT NULL,
                turma_id INTEGER REFERENCES turmas(id),
                professor_id INTEGER REFERENCES users(id),
                ordem INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de progresso dos alunos
        cur.execute('''
            CREATE TABLE IF NOT EXISTS progresso_alunos (
                id SERIAL PRIMARY KEY,
                aluno_id INTEGER REFERENCES users(id),
                aula_id INTEGER REFERENCES aulas(id),
                status VARCHAR(20) DEFAULT 'não_iniciada',
                data_inicio TIMESTAMP,
                data_conclusao TIMESTAMP,
                tempo_gasto INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de exercícios
        cur.execute('''
            CREATE TABLE IF NOT EXISTS exercicios (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(200) NOT NULL,
                pergunta TEXT NOT NULL,
                opcoes JSONB,
                resposta_correta TEXT,
                tipo VARCHAR(20) DEFAULT 'multipla_escolha',
                aula_id INTEGER REFERENCES aulas(id),
                pontos INTEGER DEFAULT 10,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de respostas dos alunos
        cur.execute('''
            CREATE TABLE IF NOT EXISTS respostas_alunos (
                id SERIAL PRIMARY KEY,
                aluno_id INTEGER REFERENCES users(id),
                exercicio_id INTEGER REFERENCES exercicios(id),
                resposta TEXT,
                esta_correta BOOLEAN,
                pontos_ganhos INTEGER DEFAULT 0,
                tempo_resposta INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        
        # Tabela de conquistas dos alunos
        cur.execute('''
            CREATE TABLE IF NOT EXISTS conquistas_alunos (
                id SERIAL PRIMARY KEY,
                aluno_id INTEGER REFERENCES users(id),
                conquista_id INTEGER REFERENCES conquistas(id),
                data_conquista TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de fórum
        cur.execute('''
            CREATE TABLE IF NOT EXISTS topicos_forum (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(200) NOT NULL,
                conteudo TEXT NOT NULL,
                autor_id INTEGER REFERENCES users(id),
                turma_id INTEGER REFERENCES turmas(id),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de comentários do fórum
        cur.execute('''
            CREATE TABLE IF NOT EXISTS comentarios_forum (
                id SERIAL PRIMARY KEY,
                topico_id INTEGER REFERENCES topicos_forum(id),
                autor_id INTEGER REFERENCES users(id),
                conteudo TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de sessões
        cur.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id VARCHAR(255) PRIMARY KEY,
                data BYTEA NOT NULL,
                expiry TIMESTAMP NOT NULL
            )
        ''')
        
        print("✅ Todas as tabelas foram criadas com sucesso!")
        
        # Criar usuário administrador padrão
        admin_password = generate_password_hash('admin123')
        cur.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, user_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        ''', ('admin', 'admin@escola.com', admin_password, 'Administrador', 'Sistema', 'admin'))
        
        # Criar usuário professor padrão
        prof_password = generate_password_hash('prof123')
        cur.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, user_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        ''', ('professor', 'prof@escola.com', prof_password, 'Professor', 'Exemplo', 'professor'))
        
        # Criar usuário aluno padrão
        aluno_password = generate_password_hash('aluno123')
        cur.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, user_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        ''', ('aluno', 'aluno@escola.com', aluno_password, 'Aluno', 'Exemplo', 'aluno'))
        
        # Criar turma de exemplo
        cur.execute('''
            INSERT INTO turmas (nome, descricao, professor_id)
            SELECT %s, %s, id FROM users WHERE username = 'professor'
            ON CONFLICT DO NOTHING
        ''', ('Turma de Exemplo', 'Turma criada automaticamente para demonstração'))
        
        # Commit das alterações
        db.commit()
        
        print("✅ Usuários padrão criados com sucesso!")
        print("📋 Credenciais dos usuários padrão:")
        print("   👑 Admin: admin / admin123")
        print("   👨‍🏫 Professor: professor / prof123")
        print("   👨‍🎓 Aluno: aluno / aluno123")
        
        cur.close()
        db.close()
        
        print("🎉 Configuração do banco de dados concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao configurar banco de dados: {e}")
        raise e

if __name__ == '__main__':
    setup_database()
