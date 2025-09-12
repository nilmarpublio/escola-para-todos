-- Schema do banco de dados para Supabase
-- Aqui se Aprende - Plataforma Educacional

-- Criar tabela users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    tipo_usuario TEXT NOT NULL DEFAULT 'aluno',
    ativo BOOLEAN NOT NULL DEFAULT true,
    data_criacao TIMESTAMP DEFAULT NOW(),
    data_atualizacao TIMESTAMP DEFAULT NOW()
);

-- Criar tabela turmas
CREATE TABLE IF NOT EXISTS turmas (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    descricao TEXT,
    professor_id INTEGER REFERENCES users(id),
    ativo BOOLEAN DEFAULT true,
    data_criacao TIMESTAMP DEFAULT NOW()
);

-- Criar tabela aulas
CREATE TABLE IF NOT EXISTS aulas (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    conteudo TEXT,
    turma_id INTEGER REFERENCES turmas(id),
    ordem INTEGER DEFAULT 0,
    ativo BOOLEAN DEFAULT true,
    data_criacao TIMESTAMP DEFAULT NOW()
);

-- Criar tabela forum_posts
CREATE TABLE IF NOT EXISTS forum_posts (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    autor_id INTEGER REFERENCES users(id),
    turma_id INTEGER REFERENCES turmas(id),
    ativo BOOLEAN DEFAULT true,
    data_criacao TIMESTAMP DEFAULT NOW()
);

-- Criar tabela gamificacao
CREATE TABLE IF NOT EXISTS gamificacao (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES users(id),
    pontos INTEGER DEFAULT 0,
    nivel INTEGER DEFAULT 1,
    conquistas TEXT[] DEFAULT '{}',
    data_atualizacao TIMESTAMP DEFAULT NOW()
);

-- Criar tabela relatorios
CREATE TABLE IF NOT EXISTS relatorios (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES users(id),
    tipo_relatorio TEXT NOT NULL,
    dados JSONB,
    data_criacao TIMESTAMP DEFAULT NOW()
);

-- Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_tipo ON users(tipo_usuario);
CREATE INDEX IF NOT EXISTS idx_turmas_professor ON turmas(professor_id);
CREATE INDEX IF NOT EXISTS idx_aulas_turma ON aulas(turma_id);
CREATE INDEX IF NOT EXISTS idx_forum_autor ON forum_posts(autor_id);
CREATE INDEX IF NOT EXISTS idx_forum_turma ON forum_posts(turma_id);
CREATE INDEX IF NOT EXISTS idx_gamificacao_usuario ON gamificacao(usuario_id);

-- Criar usuário admin padrão
INSERT INTO users (nome, username, email, password_hash, tipo_usuario)
VALUES (
    'Administrador',
    'admin',
    'admin@aqui-se-aprende.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J.8.8.8.8',
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- Criar usuário professor de exemplo
INSERT INTO users (nome, username, email, password_hash, tipo_usuario)
VALUES (
    'Professor Exemplo',
    'professor',
    'professor@aqui-se-aprende.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J.8.8.8.8',
    'professor'
) ON CONFLICT (username) DO NOTHING;

-- Criar usuário aluno de exemplo
INSERT INTO users (nome, username, email, password_hash, tipo_usuario)
VALUES (
    'Aluno Exemplo',
    'aluno',
    'aluno@aqui-se-aprende.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J.8.8.8.8',
    'aluno'
) ON CONFLICT (username) DO NOTHING;

-- Criar turma de exemplo
INSERT INTO turmas (nome, descricao, professor_id)
VALUES (
    'Matemática Básica',
    'Turma de matemática para iniciantes',
    2
);

-- Criar aula de exemplo
INSERT INTO aulas (titulo, conteudo, turma_id, ordem)
VALUES (
    'Introdução à Matemática',
    'Conceitos básicos de matemática para iniciantes',
    1,
    1
);

-- Criar post de exemplo no fórum
INSERT INTO forum_posts (titulo, conteudo, autor_id, turma_id)
VALUES (
    'Bem-vindos à turma!',
    'Sejam bem-vindos à nossa turma de matemática. Vamos aprender juntos!',
    2,
    1
);

-- Criar dados de gamificação para o aluno
INSERT INTO gamificacao (usuario_id, pontos, nivel, conquistas)
VALUES (
    3,
    0,
    1,
    '{}'
);

-- Configurar RLS (Row Level Security) se necessário
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE turmas ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE aulas ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE forum_posts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE gamificacao ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE relatorios ENABLE ROW LEVEL SECURITY;

-- Criar políticas de segurança básicas (opcional)
-- CREATE POLICY "Users can view their own data" ON users
--     FOR SELECT USING (auth.uid()::text = id::text);

-- CREATE POLICY "Users can update their own data" ON users
--     FOR UPDATE USING (auth.uid()::text = id::text);

-- CREATE POLICY "Users can insert their own data" ON users
--     FOR INSERT WITH CHECK (auth.uid()::text = id::text);

-- Comentários das tabelas
COMMENT ON TABLE users IS 'Tabela de usuários do sistema';
COMMENT ON TABLE turmas IS 'Tabela de turmas/classes';
COMMENT ON TABLE aulas IS 'Tabela de aulas/conteúdo';
COMMENT ON TABLE forum_posts IS 'Tabela de posts do fórum';
COMMENT ON TABLE gamificacao IS 'Tabela de dados de gamificação';
COMMENT ON TABLE relatorios IS 'Tabela de relatórios e analytics';

-- Comentários das colunas principais
COMMENT ON COLUMN users.tipo_usuario IS 'Tipo de usuário: admin, professor, aluno';
COMMENT ON COLUMN users.password_hash IS 'Hash da senha do usuário';
COMMENT ON COLUMN turmas.professor_id IS 'ID do professor responsável pela turma';
COMMENT ON COLUMN aulas.turma_id IS 'ID da turma à qual a aula pertence';
COMMENT ON COLUMN forum_posts.autor_id IS 'ID do autor do post';
COMMENT ON COLUMN gamificacao.pontos IS 'Pontos acumulados pelo usuário';
COMMENT ON COLUMN gamificacao.nivel IS 'Nível atual do usuário';
COMMENT ON COLUMN gamificacao.conquistas IS 'Array de conquistas desbloqueadas';
