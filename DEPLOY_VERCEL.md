# 🚀 Deploy no Vercel + Supabase - Educa Fácil

## 📋 Pré-requisitos

1. **Conta no Vercel**: [vercel.com](https://vercel.com) (gratuita)
2. **Conta no Supabase**: [supabase.com](https://supabase.com) (gratuita)
3. **GitHub**: Para conectar o repositório

## 🔧 Configuração do Supabase

### 1. Criar Projeto no Supabase
1. Acesse [supabase.com](https://supabase.com)
2. Clique em "New Project"
3. Escolha organização e nome do projeto: `educa-facil`
4. Defina senha do banco de dados
5. Escolha região: `South America (São Paulo)`
6. Clique em "Create new project"

### 2. Configurar Banco de Dados
1. Vá para **SQL Editor** no painel do Supabase
2. Execute o script SQL abaixo:

```sql
-- Criar tabela users
CREATE TABLE users (
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
CREATE TABLE turmas (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    descricao TEXT,
    professor_id INTEGER REFERENCES users(id),
    ativo BOOLEAN DEFAULT true,
    data_criacao TIMESTAMP DEFAULT NOW()
);

-- Criar tabela aulas
CREATE TABLE aulas (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    conteudo TEXT,
    turma_id INTEGER REFERENCES turmas(id),
    ordem INTEGER DEFAULT 0,
    ativo BOOLEAN DEFAULT true,
    data_criacao TIMESTAMP DEFAULT NOW()
);

-- Criar tabela forum_posts
CREATE TABLE forum_posts (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    autor_id INTEGER REFERENCES users(id),
    turma_id INTEGER REFERENCES turmas(id),
    ativo BOOLEAN DEFAULT true,
    data_criacao TIMESTAMP DEFAULT NOW()
);

-- Criar usuário admin padrão
INSERT INTO users (nome, username, email, password_hash, tipo_usuario)
VALUES (
    'Administrador',
    'admin',
    'admin@educa-facil.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J.8.8.8.8',
    'admin'
);
```

### 3. Obter Credenciais
1. Vá para **Settings** > **API**
2. Copie:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## 🚀 Deploy no Vercel

### 1. Preparar Repositório
1. Faça commit das alterações:
```bash
git add .
git commit -m "Configuração para Vercel + Supabase"
git push origin main
```

### 2. Conectar ao Vercel
1. Acesse [vercel.com](https://vercel.com)
2. Clique em "New Project"
3. Conecte seu repositório GitHub
4. Selecione o repositório `Educa-Facil`

### 3. Configurar Variáveis de Ambiente
No Vercel, vá para **Settings** > **Environment Variables**:

```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SECRET_KEY=sua-chave-secreta-super-segura
```

### 4. Configurar Build
- **Framework Preset**: Other
- **Build Command**: `pip install -r requirements_vercel.txt`
- **Output Directory**: (deixar vazio)
- **Install Command**: `pip install -r requirements_vercel.txt`

### 5. Deploy
1. Clique em "Deploy"
2. Aguarde o build completar
3. Acesse a URL fornecida

## 🌐 Acessar a Aplicação

Após o deploy, a aplicação estará disponível em:
```
https://educa-facil.vercel.app
```

## 🔍 Comandos Úteis

### Verificar Status
```bash
# Ver logs do Vercel
vercel logs

# Ver status do projeto
vercel status
```

### Deploy Local
```bash
# Instalar Vercel CLI
npm i -g vercel

# Fazer deploy local
vercel

# Deploy para produção
vercel --prod
```

## 🔧 Troubleshooting

### Problemas comuns:

1. **Erro de conexão com Supabase**
   - Verificar variáveis de ambiente
   - Verificar se o projeto Supabase está ativo

2. **Erro de build**
   - Verificar se `requirements_vercel.txt` está correto
   - Verificar se `app_vercel.py` existe

3. **Erro 500**
   - Verificar logs no Vercel
   - Verificar se as tabelas existem no Supabase

## 📊 Monitoramento

### Vercel
- **Analytics**: Tráfego e performance
- **Functions**: Logs das funções serverless
- **Deployments**: Histórico de deploys

### Supabase
- **Database**: Queries e performance
- **Auth**: Usuários e sessões
- **Storage**: Arquivos e uploads

## 💰 Custos

### Vercel (Gratuito)
- **Bandwidth**: 100GB/mês
- **Function executions**: 100GB-horas/mês
- **Build minutes**: 6000/mês

### Supabase (Gratuito)
- **Database**: 500MB
- **Bandwidth**: 2GB/mês
- **Auth users**: 50.000
- **API requests**: 500.000/mês

## 🔄 Atualizações

### Deploy de novas versões
```bash
# Deploy automático via Git
git push origin main

# Deploy manual
vercel --prod
```

### Rollback
1. Vá para **Deployments** no Vercel
2. Clique em "..." ao lado do deployment
3. Selecione "Promote to Production"

## 📞 Suporte

- **Vercel**: [vercel.com/docs](https://vercel.com/docs)
- **Supabase**: [supabase.com/docs](https://supabase.com/docs)
- **Status**: [status.vercel.com](https://status.vercel.com)

---

**🎉 Parabéns! Sua aplicação está rodando no Vercel + Supabase!**
