-- =====================================================
-- SCHEMA DO BANCO DE DADOS - ESCOLA PARA TODOS
-- Versão: 1.0
-- Data: 2024
-- =====================================================

-- 1. TABELA USERS (Usuários)
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
);

-- 2. TABELA TURMAS (Turmas escolares)
CREATE TABLE IF NOT EXISTS turmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    serie TEXT NOT NULL,
    professor_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (professor_id) REFERENCES users (id)
);

-- 3. TABELA ALUNO_TURMA (Relacionamento N:N aluno-turma)
CREATE TABLE IF NOT EXISTS aluno_turma (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER NOT NULL,
    turma_id INTEGER NOT NULL,
    data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo', 'transferido')),
    FOREIGN KEY (aluno_id) REFERENCES users (id),
    FOREIGN KEY (turma_id) REFERENCES turmas (id),
    UNIQUE(aluno_id, turma_id)
);

-- 4. TABELA AULAS (Aulas com vídeos)
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
);

-- 5. TABELA EXERCICIOS (Exercícios das aulas)
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
);

-- 6. TABELA PROGRESSO (Progresso dos alunos)
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
);

-- 7. TABELA CONQUISTAS (Sistema de conquistas)
CREATE TABLE IF NOT EXISTS conquistas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    pontos INTEGER DEFAULT 0,
    icone TEXT DEFAULT 'fas fa-trophy',
    criterio TEXT, -- critério para desbloquear
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. TABELA ALUNO_CONQUISTA (Relacionamento N:N aluno-conquista)
CREATE TABLE IF NOT EXISTS aluno_conquista (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER NOT NULL,
    conquista_id INTEGER NOT NULL,
    data_conquista TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (aluno_id) REFERENCES users (id),
    FOREIGN KEY (conquista_id) REFERENCES conquistas (id),
    UNIQUE(aluno_id, conquista_id)
);

-- 9. TABELA DISCIPLINAS (Organização por matéria)
CREATE TABLE IF NOT EXISTS disciplinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    cor TEXT DEFAULT '#007bff',
    icone TEXT DEFAULT 'fas fa-book',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ÍNDICES PARA MELHORAR PERFORMANCE
-- =====================================================

-- Índices para users
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type);

-- Índices para turmas
CREATE INDEX IF NOT EXISTS idx_turmas_professor ON turmas(professor_id);
CREATE INDEX IF NOT EXISTS idx_turmas_serie ON turmas(serie);

-- Índices para aluno_turma
CREATE INDEX IF NOT EXISTS idx_aluno_turma_aluno ON aluno_turma(aluno_id);
CREATE INDEX IF NOT EXISTS idx_aluno_turma_turma ON aluno_turma(turma_id);

-- Índices para aulas
CREATE INDEX IF NOT EXISTS idx_aulas_professor ON aulas(professor_id);
CREATE INDEX IF NOT EXISTS idx_aulas_disciplina ON aulas(disciplina);
CREATE INDEX IF NOT EXISTS idx_aulas_serie ON aulas(serie);

-- Índices para exercicios
CREATE INDEX IF NOT EXISTS idx_exercicios_aula ON exercicios(aula_id);

-- Índices para progresso
CREATE INDEX IF NOT EXISTS idx_progresso_aluno ON progresso(aluno_id);
CREATE INDEX IF NOT EXISTS idx_progresso_aula ON progresso(aula_id);
CREATE INDEX IF NOT EXISTS idx_progresso_status ON progresso(status);

-- Índices para aluno_conquista
CREATE INDEX IF NOT EXISTS idx_aluno_conquista_aluno ON aluno_conquista(aluno_id);
CREATE INDEX IF NOT EXISTS idx_aluno_conquista_conquista ON aluno_conquista(conquista_id);

-- =====================================================
-- COMENTÁRIOS SOBRE A ESTRUTURA
-- =====================================================

/*
ESTRUTURA DO BANCO:

1. USERS: Sistema de usuários com 3 tipos (aluno, professor, admin)
   - Username único para login
   - Email único para identificação
   - Senha criptografada com hash
   - Controle de status ativo/inativo

2. TURMAS: Organização das turmas escolares
   - Cada turma tem um professor responsável
   - Relacionamento 1:N com users (professor)

3. ALUNO_TURMA: Relacionamento N:N entre alunos e turmas
   - Permite que um aluno esteja em múltiplas turmas
   - Controle de status da matrícula
   - Data de matrícula para histórico

4. AULAS: Conteúdo educacional
   - Cada aula pertence a uma disciplina e série
   - Link para vídeo (YouTube, Vimeo, etc.)
   - Controle de dificuldade
   - Relacionamento com professor criador

5. EXERCICIOS: Avaliações das aulas
   - Suporte a múltiplos tipos (múltipla escolha, V/F, texto)
   - Alternativas armazenadas como JSON (texto)
   - Pontuação configurável
   - Relacionamento com aula específica

6. PROGRESSO: Acompanhamento do aprendizado
   - Status: não iniciado, em andamento, concluído
   - Tempo assistido em segundos
   - Pontuação acumulada
   - Última atividade para analytics

7. CONQUISTAS: Sistema gamificado
   - Conquistas desbloqueáveis
   - Pontos para ranking
   - Ícones personalizáveis
   - Critérios para desbloqueio

8. DISCIPLINAS: Organização curricular
   - Cores e ícones para UI
   - Descrições para contexto

RELACIONAMENTOS:
- users (1) ←→ (N) turmas (professor)
- users (N) ←→ (N) turmas (alunos via aluno_turma)
- users (1) ←→ (N) aulas (professor)
- aulas (1) ←→ (N) exercicios
- users (1) ←→ (N) progresso (aluno)
- aulas (1) ←→ (N) progresso
- users (N) ←→ (N) conquistas (via aluno_conquista)

CONSTRAINTS:
- CHECK constraints para valores válidos
- UNIQUE constraints para dados únicos
- FOREIGN KEY constraints para integridade referencial
- Índices para otimização de consultas
*/
