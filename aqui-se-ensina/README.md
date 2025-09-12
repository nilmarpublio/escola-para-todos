# 🎓 Aqui se Aprende - Sistema de Educação Digital

Uma plataforma educacional completa desenvolvida em **Flask** para democratizar o acesso à educação de qualidade, com sistema de gamificação, fórum interativo e API REST.

> **🚀 Plataforma completa com funcionalidades avançadas de educação digital!**

## 🔥 Características Principais

Esta plataforma foi desenvolvida com foco em:

- **Educação Gamificada**: Sistema de níveis, conquistas e ranking para motivar os alunos
- **Fórum Interativo**: Comunidade de aprendizado com discussões e busca
- **API REST**: Integração completa com documentação Swagger
- **Multi-banco**: Suporte a SQLite (desenvolvimento) e PostgreSQL (produção)
- **Interface Responsiva**: Design moderno e adaptável a diferentes dispositivos
- **Sistema de Progresso**: Acompanhamento detalhado do aprendizado

### ✅ Tecnologias Utilizadas:
- ✅ Flask com Flask-Login para autenticação
- ✅ SQLite/PostgreSQL com psycopg2
- ✅ Flask-RESTful para API REST
- ✅ Flask-Swagger-UI para documentação
- ✅ Sistema de gamificação completo
- ✅ Fórum com busca e categorização

## 🚀 Funcionalidades Principais

### 👥 Sistema de Usuários
- **3 Tipos de Usuário**: Alunos, Professores e Administradores
- **Perfis Personalizados**: Dashboards específicos para cada tipo
- **Gestão Completa**: Criação, edição e controle de usuários
- **Sistema de Permissões**: Controle granular de acesso

### 🎓 Gestão Educacional
- **Turmas Organizadas**: Criação e gerenciamento de turmas por série
- **Aulas Interativas**: Conteúdo com vídeos e exercícios
- **Exercícios Dinâmicos**: Sistema de avaliação com pontuação
- **Progresso Detalhado**: Acompanhamento individual e por turma

### 🏆 Sistema de Gamificação
- **Níveis de Aluno**: 5 níveis (Iniciante → Mestre)
- **Sistema de Pontos**: Pontuação por exercícios e atividades
- **Conquistas**: Badges e reconhecimentos por conquistas
- **Ranking Semanal**: Competição saudável entre alunos
- **Metas Semanais**: Objetivos personalizados de aprendizado

### 💬 Fórum Interativo
- **Discussões por Disciplina**: Organização por matéria
- **Sistema de Busca**: Encontre tópicos rapidamente
- **Criação de Tópicos**: Professores e alunos podem iniciar discussões
- **Comunidade de Aprendizado**: Interação entre todos os usuários

### 📊 Relatórios e Analytics
- **Dashboard Administrativo**: Visão geral do sistema
- **Relatórios de Turma**: Progresso e estatísticas por turma
- **Relatórios de Aluno**: Acompanhamento individual detalhado
- **Métricas de Engajamento**: Dados sobre uso da plataforma

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask 2.3.3 com Flask-Login
- **Banco de Dados**: SQLite (desenvolvimento) + PostgreSQL (produção)
- **API REST**: Flask-RESTful com documentação Swagger
- **Autenticação**: Flask-Login com sistema de permissões
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Ícones**: Font Awesome
- **Deploy**: Gunicorn + Render.com

## 📋 Pré-requisitos

- Python 3.8+
- SQLite3 (incluído no Python) ou PostgreSQL 12+
- pip (gerenciador de pacotes Python)

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd aqui-se-aprende
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

### 4. Configure as variáveis de ambiente

Copie o arquivo `env_example.txt` para `.env` e configure:
```bash
cp env_example.txt .env
```

Edite o arquivo `.env`:
```env
SECRET_KEY=sua-chave-secreta-aqui
FLASK_ENV=development
FLASK_DEBUG=1
```

### 5. Inicialize o banco de dados

**Para SQLite (desenvolvimento):**
```bash
python init_db.py
```

**Para PostgreSQL (produção):**
```bash
python init_db_postgres.py
```

### 6. Execute a aplicação

**Desenvolvimento (SQLite):**
```bash
python app.py
```

**Produção (PostgreSQL):**
```bash
python app_postgres.py
```

A aplicação estará disponível em: `http://localhost:5000`

## 👥 Usuários Padrão

### Administrador
- **Username**: admin
- **Senha**: admin123
- **Email**: admin@aqui-se-aprende.com

### Professores
- **Username**: prof.matematica / **Senha**: prof123
- **Username**: prof.portugues / **Senha**: prof123

### Alunos
- **Username**: aluno.joao / **Senha**: aluno123
- **Username**: aluno.ana / **Senha**: aluno123
- **Username**: aluno.pedro / **Senha**: aluno123

## 📁 Estrutura do Projeto

```
aqui-se-aprende/
├── app.py                    # Aplicação principal (SQLite)
├── app_postgres.py          # Aplicação para PostgreSQL
├── requirements.txt         # Dependências Python
├── init_db.py              # Inicialização SQLite
├── init_db_postgres.py     # Inicialização PostgreSQL
├── models.py               # Modelos de usuário
├── auth.py                 # Decoradores de autenticação
├── api/                    # API REST
│   ├── turmas.py          # Endpoints de turmas
│   └── swagger.py         # Documentação Swagger
├── services/               # Lógica de negócio
│   ├── turma_service.py   # Serviços de turma
│   └── ai_recommendation_service.py
├── templates/              # Templates HTML (48 arquivos)
│   ├── base.html
│   ├── splash.html
│   ├── login.html
│   ├── student_dashboard.html
│   ├── admin_dashboard.html
│   ├── professor_dashboard.html
│   ├── student_gamificacao.html
│   ├── forum.html
│   └── errors/
├── utils/                  # Utilitários
│   └── database.py
├── tests/                  # Testes automatizados
├── migrations/             # Migrações de banco
└── README.md
```

## 🔌 API REST

### Documentação Swagger
Acesse a documentação interativa da API em:
- **URL**: `http://localhost:5000/api/docs`
- **Especificação OpenAPI**: `http://localhost:5000/static/swagger.json`

### Endpoints Principais

#### Turmas
- `GET /api/turmas` - Listar todas as turmas
- `POST /api/turmas` - Criar nova turma
- `GET /api/turmas/{id}` - Obter turma específica
- `PUT /api/turmas/{id}` - Atualizar turma
- `DELETE /api/turmas/{id}` - Remover turma

#### Alunos de Turma
- `GET /api/turmas/{id}/alunos` - Listar alunos da turma

#### Progresso de Turma
- `GET /api/turmas/{id}/progresso` - Estatísticas de progresso

### Exemplo de Uso
```bash
# Listar turmas (requer autenticação)
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/turmas

# Criar nova turma
curl -X POST http://localhost:5000/api/turmas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"nome": "Turma A", "serie": 5, "professor_id": 1}'
```

## 🔧 Comandos Úteis

### Desenvolvimento
```bash
# Executar em modo desenvolvimento (SQLite)
python app.py

# Executar em modo produção (PostgreSQL)
python app_postgres.py

# Executar com Flask CLI
flask run

# Executar com debug ativado
flask run --debug
```

### Banco de Dados
```bash
# Inicializar SQLite (desenvolvimento)
python init_db.py

# Inicializar PostgreSQL (produção)
python init_db_postgres.py

# Verificar estrutura do banco
python check_tables_structure.py
```

### Testes
```bash
# Executar todos os testes
python -m pytest

# Executar testes específicos
python test_app.py
python test_auth_decorators.py
```

## 🎯 Funcionalidades Detalhadas

### 👨‍🎓 Para Estudantes
- ✅ **Dashboard Personalizado**: Visão geral do progresso e atividades
- ✅ **Sistema de Gamificação**: Níveis, pontos, conquistas e ranking
- ✅ **Aulas Interativas**: Conteúdo com vídeos e exercícios
- ✅ **Exercícios Dinâmicos**: Sistema de avaliação com feedback
- ✅ **Fórum de Discussão**: Participação em tópicos educacionais
- ✅ **Metas Semanais**: Objetivos personalizados de aprendizado
- ✅ **Histórico de Progresso**: Acompanhamento detalhado do aprendizado
- ✅ **Ranking Semanal**: Competição saudável com outros alunos

### 👨‍🏫 Para Professores
- ✅ **Dashboard de Professor**: Visão geral das turmas e alunos
- ✅ **Gestão de Turmas**: Criação e organização de turmas
- ✅ **Criação de Aulas**: Conteúdo educacional com exercícios
- ✅ **Relatórios de Turma**: Estatísticas e progresso por turma
- ✅ **Relatórios de Aluno**: Acompanhamento individual detalhado
- ✅ **Fórum de Discussão**: Moderação e participação em tópicos
- ✅ **Sistema de Pontuação**: Configuração de pontos para exercícios

### 👨‍💼 Para Administradores
- ✅ **Dashboard Administrativo**: Visão geral completa do sistema
- ✅ **Gestão de Usuários**: Criação, edição e controle de usuários
- ✅ **Relatórios Avançados**: Estatísticas detalhadas do sistema
- ✅ **Monitoramento de Progresso**: Acompanhamento global
- ✅ **Gestão de Conteúdo**: Controle sobre aulas e exercícios
- ✅ **Sistema de Permissões**: Controle granular de acesso
- ✅ **API REST**: Integração com sistemas externos

## 🚧 Próximas Funcionalidades

- [ ] Sistema de notificações em tempo real
- [ ] Chat em tempo real entre usuários
- [ ] Upload de arquivos e mídia
- [ ] Sistema de badges personalizados
- [ ] Relatórios de analytics avançados
- [ ] Aplicativo mobile (React Native)
- [ ] Integração com LMS externos
- [ ] Sistema de certificados

## 🐛 Solução de Problemas

### Erro de Conexão com Banco
**SQLite:**
- Verifique se o arquivo `escola_para_todos.db` existe
- Execute `python init_db.py` para criar o banco
- Verifique permissões de escrita na pasta

**PostgreSQL:**
- Verifique se o PostgreSQL está rodando
- Confirme as credenciais no arquivo `.env`
- Teste a conexão: `psql -h localhost -U escola_user -d escola_para_todos`

### Erro de Autenticação
- Verifique se o usuário existe no banco
- Confirme se a senha está correta
- Execute `python check_users.py` para verificar usuários

### Erro de Template
- Verifique se todos os templates estão na pasta `templates/`
- Confirme se os nomes dos templates estão corretos nas rotas
- Verifique se o Flask está configurado corretamente

### Erro de API
- Verifique se a documentação Swagger está acessível em `/api/docs`
- Confirme se o token de autenticação está válido
- Verifique os logs da aplicação para mais detalhes

### Comandos de Diagnóstico
```bash
# Verificar estrutura do banco
python check_tables_structure.py

# Verificar usuários
python check_users.py

# Testar conexão
python test_connection.py

# Executar testes
python -m pytest
```

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

## 🚀 Deploy

### Render.com (Recomendado)
1. Conecte seu repositório ao Render
2. Configure as variáveis de ambiente
3. Use o arquivo `render.yaml` para configuração automática
4. A aplicação será deployada automaticamente

### Outras Plataformas
- **Heroku**: Use o `Procfile` incluído
- **Docker**: Configure com `Dockerfile` personalizado
- **VPS**: Use Gunicorn + Nginx

## 📚 Documentação Adicional

- **[AUTH_README.md](AUTH_README.md)**: Sistema de autenticação completo
- **[DATABASE_README.md](DATABASE_README.md)**: Estrutura do banco de dados
- **[DEVELOPMENT.md](DEVELOPMENT.md)**: Guia de desenvolvimento
- **[DEPLOY_RENDER.md](DEPLOY_RENDER.md)**: Deploy no Render.com
- **[POSTGRES_README.md](POSTGRES_README.md)**: Configuração PostgreSQL

## 🙏 Agradecimentos

- **Comunidade Flask** - Framework incrível e flexível
- **Contribuidores do projeto** - Desenvolvimento colaborativo
- **Estudantes e educadores** - Feedback valioso para melhorias
- **Render.com** - Plataforma de deploy gratuita e confiável

---

**Desenvolvido com ❤️ para democratizar a educação e tornar o aprendizado mais engajante e interativo!**