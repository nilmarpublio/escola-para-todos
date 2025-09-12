# 🚀 Deploy no Fly.io - Educa Fácil

## 📋 Pré-requisitos

1. **Conta no Fly.io**: [fly.io](https://fly.io) (gratuita)
2. **Fly CLI**: Instalar o cliente de linha de comando
3. **Docker**: Para build local (opcional)

## 🔧 Instalação do Fly CLI

### Windows (PowerShell)
```powershell
# Instalar via winget
winget install fly.io

# Ou baixar diretamente
# https://fly.io/docs/hands-on/install-flyctl/
```

### Verificar instalação
```bash
fly version
```

## 🚀 Deploy Passo a Passo

### 1. Login no Fly.io
```bash
fly auth login
```

### 2. Inicializar o app
```bash
fly launch
```

**Responda as perguntas:**
- App name: `educa-facil` (ou escolha outro nome)
- Region: `gru` (São Paulo)
- PostgreSQL: `Yes` (para criar banco gratuito)

### 3. Configurar variáveis de ambiente
```bash
# Definir SECRET_KEY
fly secrets set SECRET_KEY="sua-chave-secreta-super-segura"

# Verificar configurações
fly secrets list
```

### 4. Deploy da aplicação
```bash
fly deploy
```

### 5. Verificar status
```bash
fly status
fly logs
```

## 🗄️ Configuração do Banco de Dados

### Criar banco PostgreSQL
```bash
# Se não foi criado automaticamente
fly postgres create --name educa-facil-db

# Conectar ao banco
fly postgres connect -a educa-facil-db
```

### Executar migrações
```bash
# Executar script de inicialização
fly ssh console
python init_db_postgres.py
```

## 🔍 Comandos Úteis

### Gerenciamento da aplicação
```bash
# Ver logs em tempo real
fly logs -f

# Reiniciar aplicação
fly restart

# Escalar aplicação
fly scale count 1

# Ver status detalhado
fly status --all
```

### Banco de dados
```bash
# Conectar ao banco
fly postgres connect -a educa-facil-db

# Backup do banco
fly postgres backup create -a educa-facil-db

# Ver backups
fly postgres backup list -a educa-facil-db
```

### Debugging
```bash
# SSH para dentro do container
fly ssh console

# Ver variáveis de ambiente
fly ssh console -C "env | grep -E '(DATABASE|SECRET)'"
```

## 🌐 Acessar a Aplicação

Após o deploy, a aplicação estará disponível em:
```
https://educa-facil.fly.dev
```

## 🔧 Troubleshooting

### Problemas comuns:

1. **Erro de conexão com banco**
   ```bash
   # Verificar se o banco está rodando
   fly postgres status -a educa-facil-db
   
   # Verificar variáveis de ambiente
   fly secrets list
   ```

2. **Aplicação não inicia**
   ```bash
   # Ver logs detalhados
   fly logs --all
   
   # Verificar se o Dockerfile está correto
   fly deploy --verbose
   ```

3. **Problemas de memória**
   ```bash
   # Escalar para mais recursos
   fly scale memory 512
   ```

## 📊 Monitoramento

### Métricas disponíveis
- CPU usage
- Memory usage
- Network I/O
- Disk I/O

### Acessar métricas
```bash
fly metrics
```

## 💰 Custos

### Plano gratuito inclui:
- 2.340 horas de CPU compartilhada
- 160 GB de largura de banda
- 1 instância PostgreSQL (256MB RAM)
- SSL automático

### Estimativa de uso:
- Aplicação pequena: **Gratuito**
- Aplicação média: ~$5-10/mês
- Aplicação grande: ~$20-50/mês

## 🔄 Atualizações

### Deploy de novas versões
```bash
# Deploy automático
git push origin main
fly deploy

# Deploy manual
fly deploy --local
```

### Rollback
```bash
# Voltar para versão anterior
fly releases
fly releases rollback <release-id>
```

## 📞 Suporte

- **Documentação**: [fly.io/docs](https://fly.io/docs)
- **Community**: [fly.io/community](https://fly.io/community)
- **Status**: [status.fly.io](https://status.fly.io)

---

**🎉 Parabéns! Sua aplicação está rodando no Fly.io!**
