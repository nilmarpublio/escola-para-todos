# 🚀 Deploy no Render - Escola para Todos

## 📋 Pré-requisitos

- ✅ Conta no Render (gratuita)
- ✅ Código no GitHub
- ✅ `render.yaml` configurado
- ✅ `app_postgres.py` funcionando
- ✅ `init_db_postgres.py` configurado

## 🔧 Arquivos Configurados

### 1. `render.yaml`
- ✅ Serviço web configurado
- ✅ Banco PostgreSQL configurado
- ✅ Variáveis de ambiente definidas
- ✅ `FLASK_APP` apontando para `app_postgres.py`

### 2. `start.sh`
- ✅ Inicialização do banco PostgreSQL
- ✅ Execução do gunicorn com `app_postgres:app`

### 3. `app_postgres.py`
- ✅ Todas as rotas implementadas
- ✅ Conexão com PostgreSQL configurada
- ✅ Funções auxiliares para templates
- ✅ Configuração de produção

### 4. `init_db_postgres.py`
- ✅ Criação de tabelas PostgreSQL
- ✅ Dados iniciais (usuários admin, professor, aluno)
- ✅ Estrutura completa do banco

## 🚀 Passos para Deploy

### 1. Fazer Commit e Push
```bash
git add .
git commit -m "Configuração para deploy no Render com PostgreSQL"
git push origin main
```

### 2. Conectar no Render
1. Acessar [render.com](https://render.com)
2. Fazer login/criar conta
3. Clicar em "New +" → "Blueprint"
4. Conectar com o repositório GitHub

### 3. Deploy Automático
- O Render detectará o `render.yaml`
- Criará automaticamente:
  - Serviço web Python
  - Banco PostgreSQL
  - Variáveis de ambiente

### 4. Verificar Deploy
- Acompanhar logs de build
- Verificar se o banco foi inicializado
- Testar a aplicação online

## 🔍 URLs de Teste

Após o deploy, testar:
- **Página inicial**: `https://escola-para-todos.onrender.com/`
- **Login**: `https://escola-para-todos.onrender.com/login`
- **Health check**: `https://escola-para-todos.onrender.com/health`

## 👥 Usuários de Teste

- **Admin**: `admin` / `admin123`
- **Professor**: `prof.matematica` / `prof123`
- **Aluno**: `aluno1` / `aluno123`

## 🚨 Solução de Problemas

### Erro de Conexão com Banco
- Verificar se `DATABASE_URL` está sendo passada
- Verificar logs do `init_db_postgres.py`

### Erro de Template
- Verificar se todas as rotas estão registradas
- Verificar se `get_user_type_display` está funcionando

### Erro de Build
- Verificar se `psycopg[binary]` está no requirements.txt
- Verificar se todos os imports estão funcionando

## 📊 Monitoramento

- **Logs**: Render Dashboard → Logs
- **Métricas**: Render Dashboard → Metrics
- **Banco**: Render Dashboard → Database

## 🎯 Próximos Passos

1. ✅ Fazer deploy no Render
2. ✅ Testar todas as funcionalidades
3. ✅ Configurar domínio personalizado (opcional)
4. ✅ Configurar backup automático do banco
5. ✅ Monitorar performance e logs

---

**🎉 A aplicação está pronta para deploy no Render!**
