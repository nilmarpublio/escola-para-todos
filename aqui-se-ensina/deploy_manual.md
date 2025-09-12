# 🚀 Deploy Manual - Aqui se Aprende

Como o login automático não está funcionando, aqui estão os passos manuais:

## 1. **Fazer Login no Fly.io**
```bash
# Execute este comando e siga as instruções
C:\Users\nilma\.fly\bin\flyctl.exe auth login
```

## 2. **Criar o App**
```bash
# Criar o app aqui-se-aprende
C:\Users\nilma\.fly\bin\flyctl.exe apps create aqui-se-aprende
```

## 3. **Criar Banco PostgreSQL**
```bash
# Criar banco de dados
C:\Users\nilma\.fly\bin\flyctl.exe postgres create --name aqui-se-aprende-db --region gru
```

## 4. **Configurar Secrets**
```bash
# Definir SECRET_KEY
C:\Users\nilma\.fly\bin\flyctl.exe secrets set SECRET_KEY="sua-chave-secreta-super-segura" -a aqui-se-aprende
```

## 5. **Fazer Deploy**
```bash
# Deploy da aplicação
C:\Users\nilma\.fly\bin\flyctl.exe deploy -a aqui-se-aprende
```

## 6. **Verificar Status**
```bash
# Ver status da aplicação
C:\Users\nilma\.fly\bin\flyctl.exe status -a aqui-se-aprende

# Ver logs
C:\Users\nilma\.fly\bin\flyctl.exe logs -a aqui-se-aprende
```

## 🌐 **URL da Aplicação**
Após o deploy: `https://aqui-se-aprende.fly.dev`

---

**Execute os comandos um por vez e me avise se algum der erro!**
