# 🚀 Deploy Manual - Educa Fácil

Como o login automático não está funcionando, aqui estão os passos manuais:

## 1. **Fazer Login no Fly.io**
```bash
# Execute este comando e siga as instruções
C:\Users\nilma\.fly\bin\flyctl.exe auth login
```

## 2. **Criar o App**
```bash
# Criar o app educa-facil
C:\Users\nilma\.fly\bin\flyctl.exe apps create educa-facil
```

## 3. **Criar Banco PostgreSQL**
```bash
# Criar banco de dados
C:\Users\nilma\.fly\bin\flyctl.exe postgres create --name educa-facil-db --region gru
```

## 4. **Configurar Secrets**
```bash
# Definir SECRET_KEY
C:\Users\nilma\.fly\bin\flyctl.exe secrets set SECRET_KEY="sua-chave-secreta-super-segura" -a educa-facil
```

## 5. **Fazer Deploy**
```bash
# Deploy da aplicação
C:\Users\nilma\.fly\bin\flyctl.exe deploy -a educa-facil
```

## 6. **Verificar Status**
```bash
# Ver status da aplicação
C:\Users\nilma\.fly\bin\flyctl.exe status -a educa-facil

# Ver logs
C:\Users\nilma\.fly\bin\flyctl.exe logs -a educa-facil
```

## 🌐 **URL da Aplicação**
Após o deploy: `https://educa-facil.fly.dev`

---

**Execute os comandos um por vez e me avise se algum der erro!**
