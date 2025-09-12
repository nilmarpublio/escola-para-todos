#!/usr/bin/env python3
"""
Script para inicializar o banco de dados SQLite com todas as tabelas principais
Versão Flask Puro com SQLite
"""

import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash

def create_database():
    """Criar banco de dados SQLite e todas as tabelas"""
    print("🗄️  Criando banco de dados SQLite...")
    
    # Conectar ao banco (criará se não existir)
    db = sqlite3.connect('escola_para_todos.db')
    db.row_factory = sqlite3.Row
    cur = db.cursor()
        
    try:
        # 1. Tabela Users
        print("👥 Criando tabela Users...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                user_type TEXT NOT NULL CHECK (user_type IN ('aluno', 'professor', 'admin')),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. Tabela Turmas
        print("🏫 Criando tabela Turmas...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS turmas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                serie TEXT NOT NULL,
                professor_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (professor_id) REFERENCES users (id)
            )
        ''')
        
        # 3. Tabela AlunoTurma (relacionamento N:N)
        print("📚 Criando tabela AlunoTurma...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS aluno_turma (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                turma_id INTEGER NOT NULL,
                data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo', 'transferido')),
                FOREIGN KEY (aluno_id) REFERENCES users (id),
                FOREIGN KEY (turma_id) REFERENCES turmas (id),
                UNIQUE(aluno_id, turma_id)
            )
        ''')
        
        # 4. Tabela Aulas
        print("📖 Criando tabela Aulas...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS aulas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                disciplina TEXT NOT NULL,
                serie TEXT NOT NULL,
                link_video TEXT,
                professor_id INTEGER NOT NULL,
                duracao_minutos INTEGER DEFAULT 45,
                dificuldade TEXT DEFAULT 'medio' CHECK (dificuldade IN ('facil', 'medio', 'dificil')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (professor_id) REFERENCES users (id)
            )
        ''')
        
        # 5. Tabela Exercicios
        print("✏️  Criando tabela Exercicios...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS exercicios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enunciado TEXT NOT NULL,
                alternativas TEXT NOT NULL, -- JSON como TEXT para SQLite
                resposta_correta TEXT NOT NULL,
                aula_id INTEGER NOT NULL,
                pontos INTEGER DEFAULT 10,
                tipo TEXT DEFAULT 'multipla_escolha' CHECK (tipo IN ('multipla_escolha', 'verdadeiro_falso', 'texto')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (aula_id) REFERENCES aulas (id)
            )
        ''')
        
        # 6. Tabela Progresso
        print("📊 Criando tabela Progresso...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS progresso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                aula_id INTEGER NOT NULL,
                status TEXT DEFAULT 'nao_iniciado' CHECK (status IN ('nao_iniciado', 'em_andamento', 'concluido')),
                pontuacao INTEGER DEFAULT 0,
                tempo_assistido INTEGER DEFAULT 0, -- em segundos
                ultima_atividade TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (aluno_id) REFERENCES users (id),
                FOREIGN KEY (aula_id) REFERENCES aulas (id),
                UNIQUE(aluno_id, aula_id)
            )
        ''')
        
        # 7. Tabela Conquistas
        print("🏆 Criando tabela Conquistas...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS conquistas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                descricao TEXT NOT NULL,
                pontos INTEGER DEFAULT 50,
                icone TEXT DEFAULT 'fas fa-trophy',
                criterio TEXT,
                requisitos TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 8. Tabela AlunoConquista (relacionamento N:N)
        print("🎖️  Criando tabela AlunoConquista...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS aluno_conquista (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                conquista_id INTEGER NOT NULL,
                data_conquista TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (aluno_id) REFERENCES users (id),
                FOREIGN KEY (conquista_id) REFERENCES conquistas (id),
                UNIQUE(aluno_id, conquista_id)
            )
        ''')
        
        # 9. Tabela Disciplinas
        print("📚 Criando tabela Disciplinas...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS disciplinas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                descricao TEXT,
                cor TEXT DEFAULT '#007bff',
                icone TEXT DEFAULT 'fas fa-book',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 10. Tabela Metas Semanais
        print("🎯 Criando tabela Metas Semanais...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS metas_semanais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK (tipo IN ('pontos', 'exercicios', 'aulas', 'tempo')),
                valor_meta INTEGER NOT NULL,
                pontos_recompensa INTEGER DEFAULT 50,
                recompensa_virtual TEXT,
                data_inicio DATE NOT NULL,
                data_fim DATE NOT NULL,
                ativa BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 11. Tabela Progresso Metas
        print("📈 Criando tabela Progresso Metas...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS progresso_metas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                meta_id INTEGER NOT NULL,
                valor_atual INTEGER DEFAULT 0,
                concluida BOOLEAN DEFAULT 0,
                data_conclusao TIMESTAMP,
                recompensa_coletada BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (aluno_id) REFERENCES users (id),
                FOREIGN KEY (meta_id) REFERENCES metas_semanais (id),
                UNIQUE(aluno_id, meta_id)
            )
        ''')
        
        # 12. Tabela Ranking Semanal
        print("🏅 Criando tabela Ranking Semanal...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ranking_semanal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                turma_id INTEGER NOT NULL,
                semana_inicio DATE NOT NULL,
                semana_fim DATE NOT NULL,
                aluno_id INTEGER NOT NULL,
                pontos_semana INTEGER DEFAULT 0,
                posicao INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (turma_id) REFERENCES turmas (id),
                FOREIGN KEY (aluno_id) REFERENCES users (id),
                UNIQUE(turma_id, semana_inicio, aluno_id)
            )
        ''')
        
        # 13. Tabela Histórico de Pontos
        print("💰 Criando tabela Histórico de Pontos...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS historico_pontos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                pontos INTEGER NOT NULL,
                tipo TEXT NOT NULL CHECK (tipo IN ('exercicio', 'meta', 'conquista', 'bonus', 'penalidade')),
                descricao TEXT NOT NULL,
                referencia_id INTEGER,
                referencia_tipo TEXT,
                data_ganho TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (aluno_id) REFERENCES users (id)
            )
        ''')
        
        # 14. Tabela Níveis do Aluno
        print("⭐ Criando tabela Níveis do Aluno...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS niveis_aluno (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                nivel_atual INTEGER DEFAULT 1,
                pontos_totais INTEGER DEFAULT 0,
                pontos_nivel_atual INTEGER DEFAULT 0,
                pontos_proximo_nivel INTEGER DEFAULT 100,
                titulo_nivel TEXT DEFAULT 'Iniciante',
                cor_nivel TEXT DEFAULT '#6c757d',
                icone_nivel TEXT DEFAULT 'fas fa-star',
                ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (aluno_id) REFERENCES users (id),
                UNIQUE(aluno_id)
            )
        ''')
        
        # 15. Tabela Fórum - Tópicos
        print("💬 Criando tabela Fórum - Tópicos...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS forum_topicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo VARCHAR(200) NOT NULL,
                conteudo TEXT NOT NULL,
                autor_id INTEGER NOT NULL,
                aula_id INTEGER NOT NULL,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT 1,
                tipo TEXT CHECK (tipo IN ('pergunta', 'discussao', 'anuncio')) DEFAULT 'pergunta',
                status TEXT CHECK (status IN ('aberto', 'resolvido', 'fechado')) DEFAULT 'aberto',
                visualizacoes INTEGER DEFAULT 0,
                FOREIGN KEY (autor_id) REFERENCES users (id),
                FOREIGN KEY (aula_id) REFERENCES aulas (id)
            )
        ''')
        
        # 16. Tabela Fórum - Respostas
        print("💬 Criando tabela Fórum - Respostas...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS forum_respostas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topico_id INTEGER NOT NULL,
                autor_id INTEGER NOT NULL,
                conteudo TEXT NOT NULL,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT 1,
                melhor_resposta BOOLEAN DEFAULT 0,
                FOREIGN KEY (topico_id) REFERENCES forum_topicos (id),
                FOREIGN KEY (autor_id) REFERENCES users (id)
            )
        ''')
        
        # 17. Tabela Fórum - Votos
        print("👍 Criando tabela Fórum - Votos...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS forum_votos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                topico_id INTEGER,
                resposta_id INTEGER,
                tipo TEXT CHECK (tipo IN ('positivo', 'negativo')) NOT NULL,
                data_voto DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES users (id),
                FOREIGN KEY (topico_id) REFERENCES forum_topicos (id),
                FOREIGN KEY (resposta_id) REFERENCES forum_respostas (id),
                CHECK ((topico_id IS NOT NULL AND resposta_id IS NULL) OR (topico_id IS NULL AND resposta_id IS NOT NULL))
            )
        ''')
        
        # 18. Tabela Fórum - Tags
        print("🏷️ Criando tabela Fórum - Tags...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS forum_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(50) UNIQUE NOT NULL,
                cor VARCHAR(7) DEFAULT '#007bff',
                descricao TEXT
            )
        ''')
        
        # 19. Tabela Fórum - Tópicos Tags
        print("🏷️ Criando tabela Fórum - Tópicos Tags...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS forum_topicos_tags (
                topico_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (topico_id, tag_id),
                FOREIGN KEY (topico_id) REFERENCES forum_topicos (id),
                FOREIGN KEY (tag_id) REFERENCES forum_tags (id)
            )
        ''')
        
        # Criar índices para melhor performance
        print("🔍 Criando índices...")
        cur.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_turmas_professor ON turmas(professor_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_aluno_turma_aluno ON aluno_turma(aluno_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_aluno_turma_turma ON aluno_turma(turma_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_aulas_professor ON aulas(professor_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_aulas_disciplina ON aulas(disciplina)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_aulas_serie ON aulas(serie)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_exercicios_aula ON exercicios(aula_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_progresso_aluno ON progresso(aluno_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_progresso_aula ON progresso(aula_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_aluno_conquista_aluno ON aluno_conquista(aluno_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_historico_pontos_aluno ON historico_pontos(aluno_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_ranking_semanal_turma ON ranking_semanal(turma_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_ranking_semanal_semana ON ranking_semanal(semana_inicio)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_forum_topicos_aula ON forum_topicos(aula_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_forum_topicos_autor ON forum_topicos(autor_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_forum_topicos_data ON forum_topicos(data_criacao)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_forum_respostas_topico ON forum_respostas(topico_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_forum_votos_usuario ON forum_votos(usuario_id)')
            
        db.commit()
        print("✅ Tabelas criadas com sucesso!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar tabelas: {e}")
        raise
    finally:
        cur.close()
        db.close()

def insert_sample_data():
    """Inserir dados de exemplo no banco"""
    print("📝 Inserindo dados de exemplo...")
    
    db = sqlite3.connect('escola_para_todos.db')
    db.row_factory = sqlite3.Row
    cur = db.cursor()
        
    try:
        # 1. Inserir usuários
        print("👥 Inserindo usuários...")
        usuarios_data = [
            ('admin', 'admin@escola.com', 'admin123', 'Admin', 'Sistema', 'admin'),
            ('prof.matematica', 'matematica@escola.com', 'prof123', 'João', 'Silva', 'professor'),
            ('prof.portugues', 'portugues@escola.com', 'prof123', 'Maria', 'Santos', 'professor'),
            ('aluno.joao', 'joao@escola.com', 'aluno123', 'João', 'Oliveira', 'aluno'),
            ('aluno.ana', 'ana@escola.com', 'aluno123', 'Ana', 'Costa', 'aluno'),
            ('aluno.pedro', 'pedro@escola.com', 'aluno123', 'Pedro', 'Lima', 'aluno')
        ]
        
        for user_data in usuarios_data:
            cur.execute('''
                INSERT OR IGNORE INTO users (username, email, password_hash, first_name, last_name, user_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_data[0], user_data[1], generate_password_hash(user_data[2]), user_data[3], user_data[4], user_data[5]))
        
        # 2. Inserir disciplinas
        print("📚 Inserindo disciplinas...")
        disciplinas_data = [
            ('Matemática', 'Ciência dos números e formas', '#dc3545', 'fas fa-calculator'),
            ('Português', 'Língua portuguesa e literatura', '#007bff', 'fas fa-book'),
            ('História', 'História do Brasil e do mundo', '#28a745', 'fas fa-landmark'),
            ('Geografia', 'Geografia física e humana', '#17a2b8', 'fas fa-globe'),
            ('Ciências', 'Ciências da natureza', '#ffc107', 'fas fa-flask'),
            ('Educação Física', 'Atividades físicas e esportes', '#6f42c1', 'fas fa-running')
        ]
        
        for disc_data in disciplinas_data:
            cur.execute('''
                INSERT OR IGNORE INTO disciplinas (nome, descricao, cor, icone)
                VALUES (?, ?, ?, ?)
            ''', disc_data)
        
        # 3. Inserir turmas
        print("🏫 Inserindo turmas...")
        cur.execute('SELECT id FROM users WHERE username = ?', ('prof.matematica',))
        prof_matematica_id = cur.fetchone()[0]
        
        cur.execute('SELECT id FROM users WHERE username = ?', ('prof.portugues',))
        prof_portugues_id = cur.fetchone()[0]
        
        turmas_data = [
            ('Turma A - 6º Ano', '6º Ano', prof_matematica_id),
            ('Turma B - 7º Ano', '7º Ano', prof_matematica_id),
            ('Turma C - 8º Ano', '8º Ano', prof_portugues_id)
        ]
        
        for turma_data in turmas_data:
            cur.execute('''
                INSERT OR IGNORE INTO turmas (nome, serie, professor_id)
                VALUES (?, ?, ?)
            ''', turma_data)
        
        # 4. Inserir aulas
        print("📖 Inserindo aulas...")
        aulas_data = [
            ('Introdução à Álgebra', 'Conceitos básicos de álgebra', 'Matemática', '6º Ano', 'https://youtube.com/watch?v=exemplo1', prof_matematica_id, 45),
            ('Equações do 1º Grau', 'Resolução de equações simples', 'Matemática', '7º Ano', 'https://youtube.com/watch?v=exemplo2', prof_matematica_id, 60),
            ('Gramática Básica', 'Elementos da gramática', 'Português', '6º Ano', 'https://youtube.com/watch?v=exemplo3', prof_portugues_id, 45),
            ('Interpretação de Texto', 'Como interpretar textos', 'Português', '7º Ano', 'https://youtube.com/watch?v=exemplo4', prof_portugues_id, 60),
            ('História do Brasil', 'Período colonial', 'História', '8º Ano', 'https://youtube.com/watch?v=exemplo5', prof_matematica_id, 45)
        ]
        
        for aula_data in aulas_data:
            cur.execute('''
                INSERT OR IGNORE INTO aulas (titulo, descricao, disciplina, serie, link_video, professor_id, duracao_minutos)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', aula_data)
        
        # 5. Inserir exercícios
        print("✏️  Inserindo exercícios...")
        cur.execute('SELECT id FROM aulas WHERE titulo = ?', ('Introdução à Álgebra',))
        aula_id = cur.fetchone()[0]
        
        exercicios_data = [
            ('Qual é o resultado de 2x + 3 quando x = 4?', '7|8|9|11', '11', aula_id, 10),
            ('Resolva: 3x - 6 = 12', 'x = 4|x = 5|x = 6|x = 7', 'x = 6', aula_id, 15),
            ('Simplifique: 5x + 2x', '7x|10x|5x²|7x²', '7x', aula_id, 10)
        ]
        
        for ex_data in exercicios_data:
            cur.execute('''
                INSERT OR IGNORE INTO exercicios (enunciado, alternativas, resposta_correta, aula_id, pontos)
                VALUES (?, ?, ?, ?, ?)
            ''', ex_data)
        
        # 6. Inserir conquistas
        print("🏆 Inserindo conquistas...")
        conquistas = [
            ('Primeira Aula', 'Complete sua primeira aula', 50, 'fas fa-star', 'primeira_aula'),
            ('Estudante Dedicado', 'Complete 5 aulas', 100, 'fas fa-graduation-cap', 'cinco_aulas'),
            ('Mestre do Conhecimento', 'Complete 20 aulas', 500, 'fas fa-crown', 'vinte_aulas'),
            ('Exercício Perfeito', 'Acerte 10 exercícios seguidos', 200, 'fas fa-check-circle', 'exercicios_perfeitos'),
            ('Meta Semanal', 'Complete uma meta semanal', 75, 'fas fa-bullseye', 'meta_semanal')
        ]
        
        for conquista in conquistas:
            cur.execute('''
                INSERT OR IGNORE INTO conquistas (nome, descricao, pontos, icone, criterio)
                VALUES (?, ?, ?, ?, ?)
            ''', conquista)
        
        # Inserir tags do fórum
        print("🏷️ Inserindo tags do fórum...")
        tags = [
            ('Dúvida', '#007bff', 'Perguntas sobre o conteúdo'),
            ('Exercício', '#28a745', 'Discussões sobre exercícios'),
            ('Teoria', '#17a2b8', 'Conceitos teóricos'),
            ('Dica', '#ffc107', 'Dicas e truques'),
            ('Bug', '#dc3545', 'Problemas e erros'),
            ('Sugestão', '#6f42c1', 'Sugestões de melhoria')
        ]
        
        for tag in tags:
            cur.execute('''
                INSERT OR IGNORE INTO forum_tags (nome, cor, descricao)
                VALUES (?, ?, ?)
            ''', tag)
        
        # Inserir tópicos de exemplo
        print("💬 Inserindo tópicos de exemplo...")
        topicos = [
            ('Como resolver o exercício 3?', 'Estou com dúvida na questão sobre derivadas. Alguém pode ajudar?', 1, 1, 'pergunta', 'aberto'),
            ('Dica para estudar matemática', 'Compartilhando uma técnica que me ajudou muito!', 2, 1, 'discussao', 'aberto'),
            ('Problema no sistema de login', 'Não consigo acessar minha conta. Alguém mais está com esse problema?', 3, 1, 'pergunta', 'aberto'),
            ('Sugestão de melhoria', 'Seria legal ter mais exercícios práticos', 1, 2, 'sugestao', 'aberto')
        ]
        
        for topico in topicos:
            cur.execute('''
                INSERT OR IGNORE INTO forum_topicos (titulo, conteudo, autor_id, aula_id, tipo, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', topico)
        
        # Inserir respostas de exemplo
        print("💬 Inserindo respostas de exemplo...")
        respostas = [
            (1, 2, 'Tente usar a regra da cadeia. Primeiro derive a função externa...'),
            (1, 3, 'Concordo! A regra da cadeia é essencial aqui.'),
            (2, 1, 'Excelente dica! Vou experimentar essa técnica.'),
            (3, 2, 'Já tentei limpar o cache do navegador?'),
            (4, 3, 'Ótima sugestão! Mais exercícios sempre ajudam.')
        ]
        
        for resposta in respostas:
            cur.execute('''
                INSERT OR IGNORE INTO forum_respostas (topico_id, autor_id, conteudo)
                VALUES (?, ?, ?)
            ''', resposta)
        
        # Marcar melhor resposta
        cur.execute('UPDATE forum_respostas SET melhor_resposta = 1 WHERE id = 1')
        
        # Inserir votos de exemplo
        print("👍 Inserindo votos de exemplo...")
        votos = [
            (1, 1, None, 'positivo'),  # Voto positivo no tópico 1
            (2, 1, None, 'positivo'),  # Voto positivo no tópico 2
            (3, 2, None, 'positivo'),  # Voto positivo no tópico 3
            (None, None, 1, 'positivo'),  # Voto positivo na resposta 1
            (None, None, 2, 'positivo')   # Voto positivo na resposta 2
        ]
        
        for voto in votos:
            cur.execute('''
                INSERT OR IGNORE INTO forum_votos (usuario_id, topico_id, resposta_id, tipo)
                VALUES (?, ?, ?, ?)
            ''', voto)
        
        # Associar tags aos tópicos
        print("🏷️ Associando tags aos tópicos...")
        topicos_tags = [
            (1, 1),  # Tópico 1 - Dúvida
            (1, 2),  # Tópico 1 - Exercício
            (2, 3),  # Tópico 2 - Teoria
            (2, 4),  # Tópico 2 - Dica
            (3, 5),  # Tópico 3 - Bug
            (4, 6)   # Tópico 4 - Sugestão
        ]
        
        for topico_tag in topicos_tags:
            cur.execute('''
                INSERT OR IGNORE INTO forum_topicos_tags (topico_id, tag_id)
                VALUES (?, ?)
            ''', topico_tag)
        
        # 7. Inserir metas semanais
        print("🎯 Inserindo metas semanais...")
        from datetime import datetime, timedelta
        
        hoje = datetime.now()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        
        metas_data = [
            ('Meta de Pontos', 'Ganhar 100 pontos esta semana', 'pontos', 100, 50, '🏆 Medalha de Ouro', inicio_semana.date(), fim_semana.date()),
            ('Meta de Exercícios', 'Resolver 5 exercícios corretamente', 'exercicios', 5, 75, '⭐ Estrela Dourada', inicio_semana.date(), fim_semana.date()),
            ('Meta de Aulas', 'Concluir 3 aulas', 'aulas', 3, 100, '👑 Coroa Real', inicio_semana.date(), fim_semana.date())
        ]
        
        for meta_data in metas_data:
            cur.execute('''
                INSERT OR IGNORE INTO metas_semanais (nome, descricao, tipo, valor_meta, pontos_recompensa, recompensa_virtual, data_inicio, data_fim)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', meta_data)
        
        # 8. Matricular alunos nas turmas
        print("📚 Matriculando alunos...")
        cur.execute('SELECT id FROM users WHERE username = ?', ('aluno.joao',))
        aluno_joao_id = cur.fetchone()[0]
        
        cur.execute('SELECT id FROM users WHERE username = ?', ('aluno.ana',))
        aluno_ana_id = cur.fetchone()[0]
        
        cur.execute('SELECT id FROM users WHERE username = ?', ('aluno.pedro',))
        aluno_pedro_id = cur.fetchone()[0]
        
        cur.execute('SELECT id FROM turmas WHERE nome = ?', ('Turma A - 6º Ano',))
        turma_a_id = cur.fetchone()[0]
        
        # Matricular João na Turma A
        cur.execute('''
            INSERT OR IGNORE INTO aluno_turma (aluno_id, turma_id, status)
            VALUES (?, ?, 'ativo')
        ''', (aluno_joao_id, turma_a_id))
        
        # Matricular Ana na Turma A
        cur.execute('''
            INSERT OR IGNORE INTO aluno_turma (aluno_id, turma_id, status)
            VALUES (?, ?, 'ativo')
        ''', (aluno_ana_id, turma_a_id))
        
        # Matricular Pedro na Turma A
        cur.execute('''
            INSERT OR IGNORE INTO aluno_turma (aluno_id, turma_id, status)
            VALUES (?, ?, 'ativo')
        ''', (aluno_pedro_id, turma_a_id))
        
        # 9. Inicializar níveis dos alunos
        print("⭐ Inicializando níveis dos alunos...")
        alunos_ids = [aluno_joao_id, aluno_ana_id, aluno_pedro_id]
        
        for aluno_id in alunos_ids:
            cur.execute('''
                INSERT OR IGNORE INTO niveis_aluno (aluno_id, nivel_atual, pontos_totais, pontos_nivel_atual, pontos_proximo_nivel, titulo_nivel, cor_nivel, icone_nivel)
                VALUES (?, 1, 0, 0, 100, 'Iniciante', '#6c757d', 'fas fa-star')
            ''', (aluno_id,))
        
        # 10. Inserir algumas conquistas para alunos (para demonstração)
        print("🏆 Inserindo conquistas para alunos...")
        cur.execute("SELECT id FROM conquistas WHERE nome = 'Primeiro Passo'")
        conquista_id = cur.fetchone()[0]
        
        # João ganha a conquista "Primeiro Passo"
        cur.execute('''
            INSERT OR IGNORE INTO aluno_conquista (aluno_id, conquista_id)
            VALUES (?, ?)
        ''', (aluno_joao_id, conquista_id))
        
        # 11. Inserir histórico de pontos inicial
        print("💰 Inserindo histórico de pontos inicial...")
        historico_data = [
            (aluno_joao_id, 50, 'conquista', 'Conquista: Primeiro Passo', conquista_id, 'conquista'),
            (aluno_joao_id, 10, 'exercicio', 'Exercício correto: Introdução à Álgebra', 1, 'exercicio'),
            (aluno_ana_id, 15, 'exercicio', 'Exercício correto: Introdução à Álgebra', 1, 'exercicio')
        ]
        
        for hist_data in historico_data:
            cur.execute('''
                INSERT OR IGNORE INTO historico_pontos (aluno_id, pontos, tipo, descricao, referencia_id, referencia_tipo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', hist_data)
        
        # 12. Atualizar pontos totais dos alunos
        print("📊 Atualizando pontos totais...")
        for aluno_id in alunos_ids:
            cur.execute('''
                UPDATE niveis_aluno 
                SET pontos_totais = (
                    SELECT COALESCE(SUM(pontos), 0) 
                    FROM historico_pontos 
                    WHERE aluno_id = ?
                )
                WHERE aluno_id = ?
            ''', (aluno_id, aluno_id))
        
            db.commit()
        print("✅ Dados de exemplo inseridos com sucesso!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao inserir dados: {e}")
        raise
    finally:
        cur.close()
        db.close()

def main():
    """Função principal"""
    print("🚀 Inicializando banco de dados SQLite da Escola para Todos...")
    print("=" * 70)
    
    try:
        # Criar banco e tabelas
        create_database()
        print()
        
        # Inserir dados de exemplo
        insert_sample_data()
        print()
        
        print("🎉 Inicialização concluída com sucesso!")
        print("=" * 70)
        print("📝 Estrutura do banco criada:")
        print("   • users - Usuários (alunos, professores, admin)")
        print("   • turmas - Turmas escolares")
        print("   • aluno_turma - Relacionamento aluno-turma")
        print("   • aulas - Aulas com vídeos")
        print("   • exercicios - Exercícios das aulas")
        print("   • progresso - Progresso dos alunos")
        print("   • conquistas - Sistema de conquistas")
        print("   • disciplinas - Organização por matéria")
        print("   • metas_semanais - Metas semanais")
        print("   • progresso_metas - Progresso das metas")
        print("   • ranking_semanal - Ranking dos alunos")
        print("   • historico_pontos - Histórico de pontos")
        print("   • niveis_aluno - Sistema de níveis")
        print()
        print("🔑 Credenciais de teste:")
        print("   👨‍💼 Admin: admin / admin123")
        print("   👨‍🏫 Professor Matemática: prof.matematica / prof123")
        print("   👩‍🏫 Professor Português: prof.portugues / prof123")
        print("   👨‍🎓 Aluno João: aluno.joao / aluno123")
        print("   👩‍🎓 Aluna Ana: aluno.ana / aluno123")
        print("   👨‍🎓 Aluno Pedro: aluno.pedro / aluno123")
        print()
        print("📊 Dados criados:")
        print("   • 6 usuários (1 admin, 2 professores, 3 alunos)")
        print("   • 6 disciplinas")
        print("   • 3 turmas")
        print("   • 5 aulas com exercícios")
        print("   • 5 conquistas disponíveis")
        print("   • 3 metas semanais")
        print("   • Sistema de níveis e pontos")
        print()
        print("🚀 Execute 'python app.py' para iniciar a aplicação!")
        
    except Exception as e:
        print(f"❌ Erro durante a inicialização: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
