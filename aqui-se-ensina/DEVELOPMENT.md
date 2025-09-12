# 🚀 Guia de Desenvolvimento - Aqui se Ensina

Este documento contém instruções para desenvolvedores sobre como trabalhar com o projeto e suas funcionalidades de escalabilidade.

## 📋 **Índice**

1. [Estrutura do Projeto](#estrutura-do-projeto)
2. [Configuração do Ambiente](#configuração-do-ambiente)
3. [Arquitetura de Camadas](#arquitetura-de-camadas)
4. [API REST](#api-rest)
5. [Documentação Swagger](#documentação-swagger)
6. [Testes](#testes)
7. [Boas Práticas](#boas-práticas)

## 🏗️ **Estrutura do Projeto**

```
escola_para_todos/
├── app.py                      # Aplicação principal Flask
├── models.py                   # Modelos de dados
├── auth.py                     # Autenticação e autorização
├── services/                   # Camada de serviços
│   ├── __init__.py
│   └── turma_service.py       # Lógica de negócio das turmas
├── utils/                      # Utilitários
│   ├── __init__.py
│   └── database.py            # Gerenciamento de banco de dados
├── api/                        # API REST
│   ├── __init__.py
│   ├── turmas.py              # Endpoints de turmas
│   └── swagger.py             # Documentação OpenAPI
├── tests/                      # Testes unitários
│   ├── __init__.py
│   └── test_turma_service.py  # Testes do TurmaService
├── templates/                  # Templates HTML
├── static/                     # Arquivos estáticos
├── requirements.txt            # Dependências Python
└── README.md                   # Documentação principal
```

## ⚙️ **Configuração do Ambiente**

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua-chave-secreta-aqui
FLASK_ENV=development
FLASK_DEBUG=1
```

### 3. Banco de Dados

```bash
python init_db.py
```

## 🎯 **Arquitetura de Camadas**

### **Camada de Apresentação (Templates)**
- `templates/` - Templates HTML com Jinja2
- `static/` - CSS, JavaScript e imagens

### **Camada de Controle (Routes)**
- `app.py` - Rotas principais da aplicação
- `auth.py` - Decorators de autenticação

### **Camada de Serviços (Business Logic)**
- `services/` - Lógica de negócio
- `services/turma_service.py` - Operações com turmas

### **Camada de Dados (Data Access)**
- `utils/database.py` - Gerenciamento de banco
- `models.py` - Modelos de dados

## 🔌 **API REST**

### **Endpoints Disponíveis**

#### **Turmas**
- `GET /api/turmas` - Listar todas as turmas
- `POST /api/turmas` - Criar nova turma
- `GET /api/turmas/{id}` - Obter turma específica
- `PUT /api/turmas/{id}` - Atualizar turma
- `DELETE /api/turmas/{id}` - Remover turma

#### **Alunos de Turma**
- `GET /api/turmas/{id}/alunos` - Listar alunos da turma

#### **Progresso de Turma**
- `GET /api/turmas/{id}/progresso` - Estatísticas de progresso

### **Exemplo de Uso**

```bash
# Listar turmas (requer autenticação)
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/turmas

# Criar nova turma
curl -X POST http://localhost:5000/api/turmas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"nome": "Turma A", "serie": 5, "professor_id": 1}'
```

## 📚 **Documentação Swagger**

### **Acessar Swagger UI**
- URL: `http://localhost:5000/api/docs`
- Documentação interativa da API
- Teste endpoints diretamente no navegador

### **Especificação OpenAPI**
- URL: `http://localhost:5000/static/swagger.json`
- Formato padrão para integração com ferramentas

## 🧪 **Testes**

### **Executar Testes**

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=services --cov=utils

# Executar testes específicos
pytest tests/test_turma_service.py

# Executar com verbose
pytest -v
```

### **Estrutura de Testes**

- **Fixtures**: Configurações reutilizáveis
- **Mocks**: Simulação de dependências externas
- **Cobertura**: Relatório de cobertura de código
- **Casos de Teste**: Sucesso, erro e edge cases

### **Exemplo de Teste**

```python
def test_get_turmas_with_stats_success(self, turma_service, mock_db):
    """Testa busca de turmas com estatísticas - sucesso"""
    mock_conn, mock_cursor = mock_db
    
    # Dados mockados
    mock_data = [(1, "Turma A", 5, datetime.now(), "prof1", 25, 12, 75.5)]
    mock_cursor.fetchall.return_value = mock_data
    
    # Executar método
    result = turma_service.get_turmas_with_stats()
    
    # Verificações
    assert result == mock_data
    assert len(result) == 1
```

## ✅ **Boas Práticas**

### **1. Separação de Responsabilidades**
- Cada camada tem responsabilidade específica
- Serviços contêm lógica de negócio
- Utils fornecem funcionalidades auxiliares

### **2. Tratamento de Erros**
- Try/catch em operações críticas
- Rollback automático em transações
- Logs detalhados para debugging

### **3. Validação de Dados**
- Validação de campos obrigatórios
- Sanitização de inputs SQL
- Verificação de permissões

### **4. Documentação**
- Docstrings em todas as funções
- Comentários explicativos
- Swagger/OpenAPI atualizado

### **5. Testes**
- Cobertura de código alta
- Testes de casos de erro
- Mocks para dependências externas

## 🔧 **Desenvolvimento**

### **Adicionar Novo Serviço**

1. Criar arquivo em `services/`
2. Implementar lógica de negócio
3. Adicionar testes em `tests/`
4. Documentar no Swagger

### **Adicionar Novo Endpoint**

1. Criar classe Resource em `api/`
2. Registrar na API principal
3. Documentar no Swagger
4. Adicionar testes

### **Adicionar Nova Utilidade**

1. Criar função em `utils/`
2. Documentar parâmetros e retorno
3. Adicionar testes
4. Usar em serviços quando apropriado

## 🚀 **Deploy e Produção**

### **Configurações de Produção**

```env
FLASK_ENV=production
FLASK_DEBUG=0
SESSION_COOKIE_SECURE=True
```

### **Banco de Dados**
- Usar PostgreSQL ou MySQL em produção
- Implementar migrations
- Backup automático

### **Monitoramento**
- Logs estruturados
- Métricas de performance
- Alertas de erro

## 📞 **Suporte**

Para dúvidas ou problemas:
- Criar issue no repositório
- Documentar steps para reprodução
- Incluir logs de erro
- Especificar ambiente (OS, Python, etc.)

---

**🎯 Lembre-se**: Mantenha o código limpo, documentado e testado!
