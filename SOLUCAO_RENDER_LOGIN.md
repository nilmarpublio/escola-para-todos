# 🔐 Solução para Problema de Login no Render

## 🚨 Problema Identificado

**Sintoma:** Apenas o usuário admin consegue fazer login no Render  
**Causa Provável:** Banco de dados vazio ou migração não aplicada

## 🔍 Passo 1: Verificar o Estado do Banco

### Acesse o Console do Render:

1. **Dashboard do Render** → Seu serviço PostgreSQL
2. **Clique em "Console" ou "Connect"**
3. **Cole e execute o script:** `check_render_db_console.sql`

### O que esperar:

- ✅ **Se funcionar:** Verá todas as tabelas e contagens
- ❌ **Se der erro:** Banco não existe ou está vazio

## 🛠️ Passo 2: Aplicar a Migração

### Opção A: Console do Render (Recomendado)

1. **No console do Render**, cole o conteúdo de:
   ```
   migration_script_20250829_110757.sql
   ```

2. **Execute o script completo**

3. **Verifique se funcionou:**
   ```sql
   SELECT COUNT(*) FROM users;  -- Deve retornar 8
   SELECT COUNT(*) FROM turmas; -- Deve retornar 5
   SELECT COUNT(*) FROM aulas;  -- Deve retornar 5
   ```

### Opção B: Script Python no Render

1. **Crie um arquivo temporário** no Render:
   ```python
   import psycopg
   import os
   
   # Conectar ao banco
   conn = psycopg.connect(os.getenv('DATABASE_URL'))
   
   # Ler e executar o script
   with open('migration_script_20250829_110757.sql', 'r') as f:
       script = f.read()
   
   cur = conn.cursor()
   cur.execute(script)
   conn.commit()
   print("Migração concluída!")
   ```

## 🔐 Passo 3: Testar os Logins

### Usuários para Testar:

| Usuário | Senha | Tipo |
|---------|-------|------|
| `admin` | `admin123` | Administrador |
| `professor` | `prof123` | Professor |
| `aluno` | `aluno123` | Aluno |
| `prof.matematica` | `prof123` | Professor |
| `aluno.joao` | `aluno123` | Aluno |

### Como Testar:

1. **Acesse a aplicação no Render**
2. **Tente fazer login com cada usuário**
3. **Verifique se consegue acessar os dashboards**

## 🚨 Possíveis Problemas e Soluções

### Problema 1: "Tabela não existe"
**Solução:** Execute o script de migração completo

### Problema 2: "Usuário não encontrado"
**Solução:** Verifique se a tabela `users` foi populada

### Problema 3: "Senha incorreta"
**Solução:** As senhas devem ser `123` para todos os usuários

### Problema 4: "Erro de conexão"
**Solução:** Verifique se o `DATABASE_URL` está correto

## 📋 Checklist de Verificação

- [ ] Banco tem 12 tabelas
- [ ] Tabela `users` tem 8 registros
- [ ] Tabela `turmas` tem 5 registros
- [ ] Tabela `aulas` tem 5 registros
- [ ] Login funciona para admin
- [ ] Login funciona para professor
- [ ] Login funciona para aluno
- [ ] Dashboards carregam corretamente

## 🔧 Se Nada Funcionar

### Resetar o Banco:

1. **No console do Render:**
   ```sql
   DROP SCHEMA public CASCADE;
   CREATE SCHEMA public;
   ```

2. **Executar o script de migração novamente**

3. **Verificar se as tabelas foram criadas**

## 📞 Suporte

**Se ainda houver problemas:**

1. **Verifique os logs da aplicação no Render**
2. **Confirme se o banco está acessível**
3. **Teste a conexão localmente primeiro**
4. **Use o arquivo JSON como backup se necessário**

---

**Arquivos necessários:**
- `check_render_db_console.sql` - Para verificar o banco
- `migration_script_20250829_110757.sql` - Para migrar os dados
- `RENDER_MIGRATION_README.md` - Documentação completa

**Lembre-se:** Execute primeiro o script de verificação para entender o estado atual do banco!
