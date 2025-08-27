# 🎓 Escola para Todos - Sistema de Educação Digital

Uma plataforma educacional completa desenvolvida em **Flask PURO** para democratizar o acesso à educação de qualidade.

> **⚠️ IMPORTANTE: Esta é uma versão Flask PURO, sem extensões externas!**

## 🔥 Por que Flask PURO?

Esta versão foi desenvolvida usando **apenas Flask puro** para demonstrar:

- **Controle total**: Sem dependências de extensões externas
- **Aprendizado**: Entendimento profundo de como Flask funciona
- **Simplicidade**: Menos dependências = menos problemas de compatibilidade
- **Performance**: Conexões diretas ao banco sem camadas de abstração
- **Flexibilidade**: Fácil de modificar e adaptar às necessidades específicas

### 🚫 O que NÃO usamos:
- ❌ Flask-SQLAlchemy (ORM)
- ❌ Flask-Login (autenticação)
- ❌ Flask-WTF (formulários)
- ❌ Flask-Migrate (migrações)
- ❌ Blueprints (organização de rotas)

### ✅ O que usamos:
- ✅ Flask puro com sessões nativas
- ✅ PostgreSQL direto com psycopg2
- ✅ Formulários HTML puros
- ✅ Autenticação manual
- ✅ SQL direto para consultas

## 🚀 Características

- **Sistema de Usuários**: Estudantes e administradores com perfis personalizados
- **Gestão de Aulas**: Criação e gerenciamento de conteúdo educacional
- **Sistema de Progresso**: Acompanhamento do aprendizado dos estudantes
- **Exercícios Interativos**: Sistema de avaliação e feedback
- **Interface Responsiva**: Design moderno e adaptável a diferentes dispositivos
- **Banco PostgreSQL**: Armazenamento robusto e escalável

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask 3.0 **PURO** (sem extensões)
- **Banco de Dados**: PostgreSQL nativo com psycopg2
- **Autenticação**: Sessões Flask nativas
- **Formulários**: HTML puro + JavaScript
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Ícones**: Font Awesome

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL 12+
- pip (gerenciador de pacotes Python)

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd Escola-para-todos-V2
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados PostgreSQL

Crie um banco de dados:
```sql
CREATE DATABASE escola_para_todos;
CREATE USER escola_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE escola_para_todos TO escola_user;
```

### 5. Configure as variáveis de ambiente

Copie o arquivo `env_example.txt` para `.env` e configure:
```bash
cp env_example.txt .env
```

Edite o arquivo `.env`:
```env
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=postgresql://escola_user:sua_senha@localhost:5432/escola_para_todos
```

### 6. Inicialize o banco de dados
```bash
python init_db.py
```

### 7. Execute a aplicação
```bash
python app.py
```

A aplicação estará disponível em: `http://localhost:5000`

## 👥 Usuários Padrão

### Administrador
- **Username**: admin
- **Senha**: admin123
- **Email**: admin@escola-para-todos.com

## 📁 Estrutura do Projeto

```
Escola-para-todos-V2/
├── app.py                 # Aplicação principal Flask PURO
├── requirements.txt      # Dependências Python (mínimas)
├── init_db.py           # Script de inicialização do banco
├── env_example.txt      # Exemplo de variáveis de ambiente
├── templates/            # Templates HTML
│   ├── base.html
│   ├── splash.html
│   ├── login.html
│   ├── register.html
│   ├── student_dashboard.html
│   ├── admin_dashboard.html
│   └── lesson.html
└── README.md
```

## 🔧 Comandos Úteis

### Desenvolvimento
```bash
# Executar em modo desenvolvimento
python app.py

# Executar com Flask CLI
flask run

# Executar com debug ativado
flask run --debug
```

### Banco de Dados
```bash
# O banco é criado automaticamente ao executar init_db.py
# Não há sistema de migrações - as tabelas são criadas diretamente
```

### Manutenção
```bash
# Inicializar banco (primeira vez)
python init_db.py

# Recriar banco (cuidado: apaga todos os dados)
# Delete as tabelas manualmente no PostgreSQL e execute init_db.py novamente
```

## 🎯 Funcionalidades

### Para Estudantes
- ✅ Cadastro e login
- ✅ Dashboard personalizado
- ✅ Acesso às aulas
- ✅ Sistema de progresso
- ✅ Exercícios interativos
- ✅ Histórico de atividades

### Para Administradores
- ✅ Gestão de usuários
- ✅ Criação e edição de aulas
- ✅ Estatísticas do sistema
- ✅ Monitoramento de progresso
- ✅ Relatórios de uso

## 🚧 Próximas Funcionalidades

- [ ] Sistema de notificações
- [ ] Chat em tempo real
- [ ] Upload de arquivos
- [ ] Sistema de gamificação
- [ ] Relatórios avançados
- [ ] API REST
- [ ] Aplicativo mobile

## 🐛 Solução de Problemas

### Erro de conexão com banco
- Verifique se o PostgreSQL está rodando
- Confirme as credenciais no arquivo `.env`
- Teste a conexão: `psql -h localhost -U escola_user -d escola_para_todos`

### Erro de banco
- Verifique se o banco existe
- Execute `python init_db.py` para criar as tabelas
- Em caso de problemas, delete as tabelas e execute `init_db.py` novamente

### Erro de template
- Verifique se todos os templates estão na pasta `templates/`
- Confirme se os nomes dos templates estão corretos nas rotas

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Entre em contato: [seu-email@exemplo.com]

## 🙏 Agradecimentos

- Comunidade Flask
- Contribuidores do projeto
- Estudantes e educadores que testaram a plataforma

---

**Desenvolvido com ❤️ para democratizar a educação**