# 🚀 Guia de Deploy - Aqui se Ensina

Este documento contém instruções para fazer deploy da aplicação no Render.

## 📋 **Pré-requisitos**

- Conta no [Render](https://render.com)
- Repositório Git configurado
- Aplicação funcionando localmente

## 🔧 **1. Preparar o Repositório**

### **1.1 Verificar Arquivos**
- ✅ `requirements.txt` - Dependências atualizadas
- ✅ `render.yaml` - Configuração do Render
- ✅ `app.py` - Configurações de produção
- ✅ Estrutura de pastas organizada

### **1.2 Commit e Push**
```bash
git add .
git commit -m "🚀 Preparar para deploy - Escalabilidade implementada"
git push origin main
```

## 🌐 **2. Deploy no Render**

### **2.1 Acessar Render Dashboard**
1. Acesse [dashboard.render.com](https://dashboard.render.com)
2. Faça login na sua conta

### **2.2 Conectar Repositório**
1. Clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte seu repositório Git
4. Selecione o repositório `aqui-se-ensina`

### **2.3 Configurar Serviço**
- **Name**: `aqui-se-ensina`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Plan**: `Free` (ou pago se necessário)

### **2.4 Variáveis de Ambiente**
Adicione as seguintes variáveis:
```
SECRET_KEY=<chave-secreta-gerada>
FLASK_ENV=production
FLASK_DEBUG=0
```

### **2.5 Deploy**
1. Clique em **"Create Web Service"**
2. Aguarde o build e deploy
3. Anote a URL gerada (ex: `https://aqui-se-ensina.onrender.com`)

## 🔄 **3. Atualizar URL Existente**

### **3.1 Substituir Serviço Atual**
1. No dashboard, localize o serviço atual
2. Clique em **"Settings"**
3. Em **"General"**, clique em **"Delete"**
4. Confirme a exclusão

### **3.2 Configurar Novo Serviço**
1. Use o mesmo nome: `aqui-se-ensina`
2. O Render manterá a URL: `https://aqui-se-ensina.onrender.com`

## ✅ **4. Verificar Deploy**

### **4.1 Testes Básicos**
- ✅ Página inicial carrega
- ✅ Login funciona
- ✅ API REST responde
- ✅ Swagger UI acessível

### **4.2 URLs de Teste**
- **Home**: `https://aqui-se-ensina.onrender.com/`
- **Login**: `https://aqui-se-ensina.onrender.com/login`
- **API Docs**: `https://aqui-se-ensina.onrender.com/api/docs`
- **API Turmas**: `https://aqui-se-ensina.onrender.com/api/turmas`

## 🚨 **5. Troubleshooting**

### **5.1 Erro de Build**
- Verificar `requirements.txt`
- Verificar versão do Python
- Verificar sintaxe do código

### **5.2 Erro de Runtime**
- Verificar logs no Render
- Verificar variáveis de ambiente
- Verificar configurações de produção

### **5.3 Erro de Banco**
- Verificar se `init_db.py` foi executado
- Verificar permissões de arquivo
- Verificar caminho do banco

## 📊 **6. Monitoramento**

### **6.1 Logs**
- Acesse **"Logs"** no dashboard
- Monitore erros e warnings
- Configure alertas se necessário

### **6.2 Métricas**
- **Uptime**: Verificar disponibilidade
- **Performance**: Tempo de resposta
- **Erros**: Taxa de erro

## 🔄 **7. Deploy Contínuo**

### **7.1 Auto-deploy**
- O Render faz deploy automático a cada push
- Configure branch principal (main/master)
- Teste sempre localmente antes do push

### **7.2 Rollback**
- Em caso de problemas, volte para commit anterior
- Use **"Manual Deploy"** se necessário
- Mantenha versões estáveis

## 🎯 **8. Próximos Passos**

### **8.1 Domínio Customizado**
- Configure domínio próprio se necessário
- Configure SSL/HTTPS
- Configure CDN se necessário

### **8.2 Escalabilidade**
- Monitorar uso de recursos
- Considerar upgrade de plano
- Implementar cache e otimizações

---

**🎉 Parabéns!** Sua aplicação está pronta para produção com todas as funcionalidades de escalabilidade!
