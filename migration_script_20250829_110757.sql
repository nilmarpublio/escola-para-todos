-- Script de migração para Render
-- Gerado automaticamente

-- Tabela: aulas
-- 5 registros

INSERT INTO aulas (id, titulo, descricao, conteudo, turma_id, professor_id, ordem, is_active, created_at, updated_at) VALUES (11, 'Contando até 10', 'Aprenda a contar de 1 a 10 de forma divertida!', 'Nesta aula você vai aprender a contar de 1 a 10 através de músicas e brincadeiras. Vamos usar objetos do dia a dia para praticar!', 8, 2, 1, true, 2025-08-28 09:27:28.368979, 2025-08-28 09:27:28.368979);
INSERT INTO aulas (id, titulo, descricao, conteudo, turma_id, professor_id, ordem, is_active, created_at, updated_at) VALUES (12, 'Vogais A, E, I, O, U', 'Conheça as vogais através de músicas e histórias', 'Vamos descobrir as vogais de forma divertida! Cada vogal tem sua música especial e vamos praticar com palavras simples.', 9, 2, 1, true, 2025-08-28 09:27:28.368979, 2025-08-28 09:27:28.368979);
INSERT INTO aulas (id, titulo, descricao, conteudo, turma_id, professor_id, ordem, is_active, created_at, updated_at) VALUES (13, 'Animais da Fazenda', 'Descubra os animais e seus sons', 'Nesta aula vamos conhecer os animais da fazenda: vaca, galinha, porco, cavalo e muito mais! Cada animal tem seu som característico.', 10, 2, 1, true, 2025-08-28 09:27:28.368979, 2025-08-28 09:27:28.368979);
INSERT INTO aulas (id, titulo, descricao, conteudo, turma_id, professor_id, ordem, is_active, created_at, updated_at) VALUES (14, 'Soma Simples', 'Aprenda a somar números pequenos', 'Vamos aprender a somar números de 1 a 10 usando objetos visuais e exercícios práticos.', 8, 2, 2, true, 2025-08-28 09:27:28.368979, 2025-08-28 09:27:28.368979);
INSERT INTO aulas (id, titulo, descricao, conteudo, turma_id, professor_id, ordem, is_active, created_at, updated_at) VALUES (15, 'Cores Primárias', 'Vermelho, azul e amarelo - as cores básicas', 'Descubra as cores primárias e como elas se misturam para formar outras cores! Vamos pintar e brincar muito!', 9, 2, 2, true, 2025-08-28 09:27:28.368979, 2025-08-28 09:27:28.368979);

-- Tabela: exercicios
-- 5 registros

INSERT INTO exercicios (id, titulo, pergunta, opcoes, resposta_correta, tipo, aula_id, pontos, is_active, created_at) VALUES (6, 'Contando Dedos', 'Quantos dedos você tem em uma mão?', {'A': '3 dedos', 'B': '5 dedos', 'C': '7 dedos', 'D': '10 dedos'}, 'B', 'multipla_escolha', 11, 10, true, 2025-08-28 09:27:28.368979);
INSERT INTO exercicios (id, titulo, pergunta, opcoes, resposta_correta, tipo, aula_id, pontos, is_active, created_at) VALUES (7, 'Vogais do Alfabeto', 'Quantas vogais existem no alfabeto?', {'A': '3 vogais', 'B': '5 vogais', 'C': '7 vogais', 'D': '26 vogais'}, 'B', 'multipla_escolha', 12, 15, true, 2025-08-28 09:27:28.368979);
INSERT INTO exercicios (id, titulo, pergunta, opcoes, resposta_correta, tipo, aula_id, pontos, is_active, created_at) VALUES (8, 'Sons dos Animais', 'Qual animal faz "muuu"?', {'A': 'Cachorro', 'B': 'Gato', 'C': 'Vaca', 'D': 'Galinha'}, 'C', 'multipla_escolha', 13, 10, true, 2025-08-28 09:27:28.368979);
INSERT INTO exercicios (id, titulo, pergunta, opcoes, resposta_correta, tipo, aula_id, pontos, is_active, created_at) VALUES (9, 'Soma Simples', 'Quanto é 2 + 3?', {'A': '4', 'B': '5', 'C': '6', 'D': '7'}, 'B', 'multipla_escolha', 14, 10, true, 2025-08-28 09:27:28.368979);
INSERT INTO exercicios (id, titulo, pergunta, opcoes, resposta_correta, tipo, aula_id, pontos, is_active, created_at) VALUES (10, 'Cores Primárias', 'Qual cor é a mistura de azul e amarelo?', {'A': 'Vermelho', 'B': 'Verde', 'C': 'Roxo', 'D': 'Laranja'}, 'B', 'multipla_escolha', 15, 15, true, 2025-08-28 09:27:28.368979);

-- Tabela: matriculas
-- 3 registros

INSERT INTO matriculas (id, aluno_id, turma_id, data_matricula, status) VALUES (4, 3, 8, 2025-08-28 09:27:28.368979, 'ativa');
INSERT INTO matriculas (id, aluno_id, turma_id, data_matricula, status) VALUES (5, 3, 9, 2025-08-28 09:27:28.368979, 'ativa');
INSERT INTO matriculas (id, aluno_id, turma_id, data_matricula, status) VALUES (6, 3, 10, 2025-08-28 09:27:28.368979, 'ativa');

-- Tabela: progresso_alunos
-- 3 registros

INSERT INTO progresso_alunos (id, aluno_id, aula_id, status, data_inicio, data_conclusao, tempo_gasto, created_at, updated_at) VALUES (1, 3, 11, 'iniciada', 2025-08-28 09:27:28.368979, NULL, 0, 2025-08-28 09:27:28.368979, 2025-08-28 09:27:28.368979);
INSERT INTO progresso_alunos (id, aluno_id, aula_id, status, data_inicio, data_conclusao, tempo_gasto, created_at, updated_at) VALUES (2, 3, 12, 'em_progresso', 2025-08-28 09:27:28.368979, NULL, 0, 2025-08-28 09:27:28.368979, 2025-08-28 09:27:28.368979);
INSERT INTO progresso_alunos (id, aluno_id, aula_id, status, data_inicio, data_conclusao, tempo_gasto, created_at, updated_at) VALUES (3, 3, 13, 'concluida', 2025-08-28 09:27:28.368979, NULL, 0, 2025-08-28 09:27:28.368979, 2025-08-28 09:27:28.368979);

-- Tabela: turmas
-- 5 registros

INSERT INTO turmas (id, nome, descricao, professor_id, max_alunos, is_active, created_at, updated_at) VALUES (1, 'Turma de Exemplo', 'Turma criada automaticamente para demonstração', 2, 30, true, 2025-08-28 07:47:20.321600, 2025-08-28 07:47:20.321600);
INSERT INTO turmas (id, nome, descricao, professor_id, max_alunos, is_active, created_at, updated_at) VALUES (8, 'Matemática Básica', 'Fundamentos da matemática para iniciantes', 2, 30, true, 2025-08-28 09:27:28.368979, 2025-08-28 09:27:28.368979);
INSERT INTO turmas (id, nome, descricao, professor_id, max_alunos, is_active, created_at, updated_at) VALUES (9, 'Português Infantil', 'Alfabetização e linguagem para crianças', 2, 25, true, 2025-08-28 09:27:28.368979, 2025-08-28 09:27:28.368979);
INSERT INTO turmas (id, nome, descricao, professor_id, max_alunos, is_active, created_at, updated_at) VALUES (10, 'Ciências Divertidas', 'Explorando o mundo das ciências', 2, 28, true, 2025-08-28 09:27:28.368979, 2025-08-28 09:27:28.368979);
INSERT INTO turmas (id, nome, descricao, professor_id, max_alunos, is_active, created_at, updated_at) VALUES (11, 'Turma de Exemplo', 'Turma criada automaticamente para demonstração', 2, 30, true, 2025-08-29 10:17:23.280558, 2025-08-29 10:17:23.280558);

-- Tabela: users
-- 8 registros

INSERT INTO users (id, username, email, password_hash, first_name, last_name, user_type, is_active, created_at, updated_at) VALUES (2, 'professor', 'prof@escola.com', 'pbkdf2:sha256:600000$F4EKWchwsBQ6ZqLK$5701117b15c17d4d711d6e2e210b360aca3b917539d45a9ca87cd00de7d17924', 'Professor', 'Exemplo', 'professor', true, 2025-08-28 07:47:20.321600, 2025-08-28 07:47:20.321600);
INSERT INTO users (id, username, email, password_hash, first_name, last_name, user_type, is_active, created_at, updated_at) VALUES (3, 'aluno', 'aluno@escola.com', 'pbkdf2:sha256:600000$SBYcCMUKnDYgkP9M$0f95b4d062ebdda93b01be460ad9fa94bc613d6077d64975c1ab799e39cfbd32', 'Aluno', 'Exemplo', 'aluno', true, 2025-08-28 07:47:20.321600, 2025-08-28 07:47:20.321600);
INSERT INTO users (id, username, email, password_hash, first_name, last_name, user_type, is_active, created_at, updated_at) VALUES (1, 'admin', 'admin@escola.com', 'pbkdf2:sha256:600000$1xi7GFrku55wa54f$026b894c935fba88ed12ecea16b58056ef3f40a79140b32c5e656fd1a814cc71', 'Admin', 'Sistema', 'admin', true, 2025-08-28 07:47:20.321600, 2025-08-28 07:47:20.321600);
INSERT INTO users (id, username, email, password_hash, first_name, last_name, user_type, is_active, created_at, updated_at) VALUES (8, 'prof.matematica', 'joao.silva@escola.com', 'pbkdf2:sha256:600000$9rfpOHGqalsp7KQy$00c29bc9a10ff669422b49356f8a26672bc5c5c39f32102ef0f8b326d3d34d98', 'João', 'Silva', 'professor', true, 2025-08-29 10:32:13.728885, 2025-08-29 10:32:13.728885);
INSERT INTO users (id, username, email, password_hash, first_name, last_name, user_type, is_active, created_at, updated_at) VALUES (9, 'prof.portugues', 'maria.santos@escola.com', 'pbkdf2:sha256:600000$DCdiMfVZ0abtePwC$86242ca345fe8a06c9550406de1f7fe92641cd8473cd2cc903726fde5cddcc51', 'Maria', 'Santos', 'professor', true, 2025-08-29 10:32:13.728885, 2025-08-29 10:32:13.728885);
INSERT INTO users (id, username, email, password_hash, first_name, last_name, user_type, is_active, created_at, updated_at) VALUES (10, 'aluno.joao', 'joao.pereira@escola.com', 'pbkdf2:sha256:600000$X3hoeSyGVEKBBcq4$8f2edbe0c3b437701868531aedb25fdf7ee5d9f7576e6007d2d17f5895b42f9e', 'João', 'Pereira', 'aluno', true, 2025-08-29 10:32:13.728885, 2025-08-29 10:32:13.728885);
INSERT INTO users (id, username, email, password_hash, first_name, last_name, user_type, is_active, created_at, updated_at) VALUES (11, 'aluno.ana', 'ana.costa@escola.com', 'pbkdf2:sha256:600000$fztkU6WjQbtZp5am$3c70c21717e951b0da198d34ca7116a9115a35d5daeb545a007ccd4f90430400', 'Ana', 'Costa', 'aluno', true, 2025-08-29 10:32:13.728885, 2025-08-29 10:32:13.728885);
INSERT INTO users (id, username, email, password_hash, first_name, last_name, user_type, is_active, created_at, updated_at) VALUES (12, 'aluno.pedro', 'pedro.oliveira@escola.com', 'pbkdf2:sha256:600000$b7gixkRBnniVhukf$6e318095824442070dcbf1e73b8e059e312812860c5536ea2d9cc35d78c55b6b', 'Pedro', 'Oliveira', 'aluno', true, 2025-08-29 10:32:13.728885, 2025-08-29 10:32:13.728885);
