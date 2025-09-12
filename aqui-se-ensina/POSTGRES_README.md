# 🗄️ PostgreSQL - Aqui se Ensina

## 📋 **Visão Geral**

Este projeto foi configurado para usar **PostgreSQL** como banco de dados principal, tanto para desenvolvimento local quanto para produção no Render.

## 🚀 **Configuração Rápida**

### **1. Desenvolvimento Local**

#### **Instalar PostgreSQL:**
- **Windows**: [Download oficial](https://www.postgresql.org/download/windows/)
- **macOS**: `brew install postgresql`
- **Linux**: `sudo apt-get install postgresql postgresql-contrib`

#### **Configurar automaticamente:**
```bash
python setup_postgres_local.py
```

#### **Configurar manualmente:**
```bash
# Criar usuário
sudo -u postgres createuser --interactive --pwprompt escola_user

# Criar banco
sudo -u postgres createdb -O escola_user escola_para_todos

# Conceder privilégios
sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE escola_para_todos TO escola_user;'
```

#### **Configurar arquivo .env:**
```bash
# Copiar exemplo
cp env_postgres.txt .env

# Editar senha se necessário
nano .env
```

### **2. Produção no Render**

O Render configurará automaticamente:
- ✅ Banco PostgreSQL gratuito (1GB)
- ✅ Variáveis de ambiente
- ✅ Conexão segura
- ✅ Backup automático

## 🔧 **Arquivos de Configuração**

### **Aplicação Principal:**
- `app_postgres.py` - Versão com PostgreSQL
- `models_postgres.py` - Modelos otimizados
- `init_db_postgres.py` - Inicialização do banco

### **Deploy:**
- `render.yaml` - Configuração do Render
- `start.sh` - Script de inicialização
- `requirements.txt` - Dependências (já inclui psycopg)

## 📊 **Estrutura do Banco**

### **Tabelas Principais:**
- `users` - Sistema de usuários
- `turmas` - Organização escolar
- `aulas` - Conteúdo educacional
- `exercicios` - Avaliações
- `progresso` - Acompanhamento
- `conquistas` - Sistema gamificado

### **Vantagens do PostgreSQL:**
- ✅ **Relacionamentos robustos** com FOREIGN KEYs
- ✅ **Constraints avançadas** (CHECK, UNIQUE, NOT NULL)
- ✅ **Índices otimizados** para performance
- ✅ **Suporte a JSON** nativo
- ✅ **Transações ACID** completas
- ✅ **Escalabilidade** para produção

## 🚀 **Como Executar**

### **Desenvolvimento Local:**
```bash
# 1. Configurar banco
python setup_postgres_local.py

# 2. Inicializar banco
python init_db_postgres.py

# 3. Executar aplicação
python app_postgres.py
```

### **Produção no Render:**
```bash
# 1. Commit das alterações
git add .
git commit -m "🚀 Configurar PostgreSQL para produção"
git push origin main

# 2. O Render fará deploy automático
# 3. Banco será criado automaticamente
```

## 🔍 **Verificar Funcionamento**

### **Local:**
- Acesse: `http://localhost:5000`
- Banco: `psql -h localhost -U escola_user -d escola_para_todos`

### **Render:**
- Acesse: `https://aqui-se-ensina.onrender.com`
- Banco: Gerenciado pelo Render

## 🛠️ **Comandos Úteis**

### **PostgreSQL:**
```bash
# Conectar ao banco
psql -h localhost -U escola_user -d escola_para_todos

# Listar tabelas
\dt

# Ver estrutura de uma tabela
\d users

# Sair
\q
```

### **Python:**
```python
# Testar conexão
python -c "
import psycopg
from dotenv import load_dotenv
import os

load_dotenv()
conn = psycopg.connect(os.getenv('DATABASE_URL'))
print('✅ Conexão PostgreSQL funcionando!')
conn.close()
"
```

## 🚨 **Troubleshooting**

### **Erro de Conexão:**
- Verificar se PostgreSQL está rodando
- Verificar credenciais no arquivo .env
- Verificar se o banco existe

### **Erro de Permissão:**
- Verificar se o usuário tem privilégios
- Verificar se o banco foi criado corretamente

### **Erro no Render:**
- Verificar logs no dashboard
- Verificar se DATABASE_URL está configurada
- Verificar se o banco foi criado

## 📈 **Próximos Passos**

1. **Testar localmente** com PostgreSQL
2. **Fazer deploy** no Render
3. **Migrar dados** do SQLite (se necessário)
4. **Otimizar queries** para PostgreSQL
5. **Implementar backup** automático

## 🎯 **Benefícios da Migração**

- ✅ **Escalabilidade** para produção
- ✅ **Performance** superior
- ✅ **Confiabilidade** empresarial
- ✅ **Suporte** oficial do Render
- ✅ **Backup** automático
- ✅ **Monitoramento** avançado

---

**🎉 PostgreSQL configurado com sucesso!**  
**🚀 Pronto para desenvolvimento e produção!**
