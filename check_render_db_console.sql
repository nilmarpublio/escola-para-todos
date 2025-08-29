-- Script para verificar o estado do banco no Render
-- Execute este script diretamente no console do Render

-- 1. Verificar tabelas existentes
SELECT 
    table_name, 
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
ORDER BY table_name;

-- 2. Verificar contagem de registros nas tabelas principais
SELECT 'users' as tabela, COUNT(*) as total FROM users
UNION ALL
SELECT 'turmas', COUNT(*) FROM turmas
UNION ALL
SELECT 'aulas', COUNT(*) FROM aulas
UNION ALL
SELECT 'exercicios', COUNT(*) FROM exercicios
UNION ALL
SELECT 'matriculas', COUNT(*) FROM matriculas
UNION ALL
SELECT 'progresso_alunos', COUNT(*) FROM progresso_alunos;

-- 3. Verificar usuários existentes
SELECT id, username, user_type, email, is_active, created_at
FROM users
ORDER BY user_type, username;

-- 4. Verificar estrutura da tabela users
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- 5. Verificar relacionamentos turmas -> aulas
SELECT 
    t.id as turma_id,
    t.nome as turma_nome,
    COUNT(a.id) as total_aulas
FROM turmas t
LEFT JOIN aulas a ON t.id = a.turma_id
GROUP BY t.id, t.nome
ORDER BY t.nome;

-- 6. Verificar se há dados de exemplo
SELECT 'Aulas de exemplo' as tipo, COUNT(*) as total
FROM aulas 
WHERE titulo LIKE '%Contando%' OR titulo LIKE '%Vogais%' OR titulo LIKE '%Animais%';

-- 7. Verificar usuários de teste específicos
SELECT username, user_type, email, is_active
FROM users 
WHERE username IN ('admin', 'professor', 'aluno', 'prof.matematica', 'aluno.joao')
ORDER BY username;

-- 8. Verificar se as senhas estão hasheadas corretamente
SELECT username, 
       CASE 
           WHEN password_hash LIKE 'pbkdf2:sha256:%' THEN 'Hash válido'
           ELSE 'Hash inválido'
       END as status_senha,
       LENGTH(password_hash) as tamanho_hash
FROM users
ORDER BY username;
