# 🔐 Sistema de Autenticação - EduApp

## 📋 Visão Geral

Este documento descreve o sistema completo de autenticação e autorização implementado na aplicação **EduApp**, incluindo login, registro, controle de acesso e gerenciamento de usuários.

## 🏗️ Arquitetura do Sistema

### **Tecnologias Utilizadas**
- **Flask-Login**: Gerenciamento de sessões e autenticação
- **bcrypt**: Criptografia de senhas
- **SQLite**: Banco de dados com modelo User personalizado
- **Werkzeug**: Utilitários de segurança

### **Componentes Principais**
1. **`models.py`**: Classe User com Flask-Login
2. **`auth.py`**: Decoradores de autorização
3. **`app.py`**: Rotas e lógica de autenticação
4. **`config.py`**: Configurações de segurança

## 👥 Modelo de Usuário

### **Classe User (Flask-Login)**
```python
class User(UserMixin):
    def __init__(self, id, username, email, first_name, last_name, user_type, is_active=True, created_at=None, updated_at=None):
        # Propriedades básicas
        self.id = id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.user_type = user_type
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
```

### **Tipos de Usuário**
- **`aluno`**: Estudantes que acessam conteúdo
- **`professor`**: Educadores que criam conteúdo
- **`admin`**: Administradores do sistema

### **Propriedades de Verificação**
```python
@property
def is_admin(self):
    return self.user_type == 'admin'

@property
def is_professor(self):
    return self.user_type == 'professor'

@property
def is_aluno(self):
    return self.user_type == 'aluno'
```

## 🛡️ Sistema de Permissões

### **Verificações de Acesso**
```python
def can_access_admin_panel(self):
    return self.is_admin

def can_create_content(self):
    return self.is_admin or self.is_professor

def can_manage_users(self):
    return self.is_admin

def can_view_analytics(self):
    return self.is_admin or self.is_professor
```

### **Permissões por Tipo**
- **Aluno**: `view_content`, `view_own_progress`, `take_exercises`
- **Professor**: `view_content`, `create_content`, `view_analytics`, `manage_own_content`
- **Admin**: Todas as permissões + `manage_users`, `manage_all_content`, `system_admin`

## 🔒 Decoradores de Autorização

### **Decoradores Disponíveis**
```python
@admin_required          # Apenas administradores
@professor_required      # Professores ou administradores
@aluno_required          # Apenas alunos
@content_creator_required # Pode criar conteúdo
@user_management_required # Pode gerenciar usuários
@analytics_required      # Pode visualizar analytics
@owner_or_admin_required # Dono do recurso ou admin
@permission_required     # Permissão específica
@active_user_required    # Usuário ativo
@guest_required          # Usuário NÃO logado
```

### **Exemplo de Uso**
```python
@app.route('/admin/users')
@user_management_required
def manage_users():
    """Gerenciar usuários (apenas admin)"""
    # ... código da função
```

## 🚪 Sistema de Login

### **Fluxo de Autenticação**
1. **Formulário de Login**: Username + senha
2. **Validação**: Verificar credenciais no banco
3. **Verificação de Status**: Conta deve estar ativa
4. **Login**: `login_user()` do Flask-Login
5. **Redirecionamento**: Baseado no tipo de usuário

### **Configuração do Flask-Login**
```python
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '🔐 Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    return User.get_by_id(int(user_id), db)
```

### **Sessões e Segurança**
- **Duração**: 24 horas (configurável)
- **Remember Me**: Opção para manter logado
- **Cookies Seguros**: HTTPOnly, SameSite
- **Secret Key**: Configurável via variável de ambiente

## 📝 Sistema de Registro

### **Registro de Alunos**
- **Acesso Livre**: Alunos podem se registrar
- **Validações**: Username único, email único, senha mínima
- **Tipo Fixo**: Apenas tipo 'aluno' permitido

### **Registro de Professores/Admins**
- **Acesso Restrito**: Apenas administradores podem criar
- **Validações**: Mesmas regras de alunos
- **Controle**: Interface administrativa

### **Validações de Segurança**
```python
# Senha mínima
if len(password) < 6:
    flash('❌ A senha deve ter pelo menos 6 caracteres.', 'error')

# Confirmação de senha
if password != confirm_password:
    flash('❌ As senhas não coincidem.', 'error')

# Username único
if User.get_by_username(username, db):
    flash('❌ Este username já está em uso.', 'error')
```

## 🔑 Gerenciamento de Senhas

### **Criptografia**
- **Algoritmo**: bcrypt
- **Hash**: Geração automática com salt
- **Verificação**: `check_password_hash()`

### **Alteração de Senha**
```python
@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    # Verificar senha atual
    if not check_password_hash(current_user.password_hash, current_password):
        flash('❌ Senha atual incorreta.', 'error')
        return render_template('change_password.html')
    
    # Alterar para nova senha
    current_user.change_password(new_password, db)
```

## 👤 Gerenciamento de Perfis

### **Edição de Perfil**
- **Campos Editáveis**: Nome, sobrenome, email
- **Validações**: Campos obrigatórios
- **Atualização**: Timestamp automático

### **Ativação/Desativação**
```python
@app.route('/admin/users/<int:user_id>/toggle-status')
@user_management_required
def toggle_user_status(user_id):
    # Verificar se não é o próprio usuário
    if user.id == current_user.id:
        flash('❌ Você não pode desativar sua própria conta.', 'error')
        return redirect(url_for('manage_users'))
    
    # Alternar status
    if user.is_active:
        user.deactivate(db)
    else:
        user.activate(db)
```

## 🎯 Controle de Acesso por Rota

### **Rotas Públicas**
- `/` - Página inicial (splash)
- `/login` - Formulário de login
- `/register` - Formulário de registro

### **Rotas Autenticadas**
- `/profile` - Perfil do usuário
- `/profile/edit` - Editar perfil
- `/change-password` - Alterar senha
- `/logout` - Sair do sistema

### **Rotas com Autorização Específica**
- `/admin` - Dashboard admin (`@admin_required`)
- `/professor` - Dashboard professor (`@professor_required`)
- `/student` - Dashboard aluno (`@aluno_required`)
- `/admin/users` - Gerenciar usuários (`@user_management_required`)

## 🚨 Tratamento de Erros

### **Páginas de Erro**
- **404**: Página não encontrada
- **403**: Acesso negado
- **500**: Erro interno do servidor

### **Mensagens Flash**
- **Sucesso**: ✅ Verde
- **Erro**: ❌ Vermelho
- **Info**: ℹ️ Azul

### **Redirecionamentos de Segurança**
```python
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash('❌ Acesso negado. Você precisa ser administrador.', 'error')
            return redirect(url_for('splash'))
        return f(*args, **kwargs)
    return decorated_function
```

## 🔧 Configurações de Segurança

### **Variáveis de Ambiente**
```bash
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=True  # Em produção com HTTPS
```

### **Configurações de Sessão**
```python
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas
app.config['SESSION_COOKIE_SECURE'] = False       # True em produção
app.config['SESSION_COOKIE_HTTPONLY'] = True      # Proteção XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'     # Proteção CSRF
```

## 📱 Interface do Usuário

### **Navbar Dinâmica**
- **Usuários Logados**: Menu personalizado por tipo
- **Usuários Anônimos**: Botões de login/registro
- **Indicador de Status**: Nome e tipo do usuário

### **Dropdown de Usuário**
- Meu Perfil
- Editar Perfil
- Alterar Senha
- Sair

### **Navegação Contextual**
- **Admin**: Dashboard, Usuários
- **Professor**: Dashboard Professor
- **Aluno**: Dashboard Aluno

## 🧪 Testes e Validação

### **Credenciais de Teste**
```
👨‍💼 Admin: admin / admin123
👨‍🏫 Professor: prof.matematica / prof123
👩‍🏫 Professor: prof.portugues / prof123
👨‍🎓 Aluno: aluno.joao / aluno123
👩‍🎓 Aluna: aluno.ana / aluno123
👨‍🎓 Aluno: aluno.pedro / aluno123
```

### **Cenários de Teste**
1. **Login com credenciais válidas**
2. **Login com credenciais inválidas**
3. **Registro de novo aluno**
4. **Tentativa de registro como professor**
5. **Acesso a rotas restritas**
6. **Edição de perfil**
7. **Alteração de senha**
8. **Logout e limpeza de sessão**

## 🚀 Como Usar

### **1. Instalar Dependências**
```bash
pip install Flask-Login==0.6.3 bcrypt==4.1.2
```

### **2. Configurar Variáveis de Ambiente**
```bash
export SECRET_KEY="sua-chave-secreta-aqui"
export FLASK_DEBUG="False"
```

### **3. Executar a Aplicação**
```bash
python app.py
```

### **4. Acessar o Sistema**
- **URL**: `http://localhost:5000`
- **Login**: `/login`
- **Registro**: `/register`

## 🔮 Próximos Passos

### **Melhorias de Segurança**
1. **Implementar 2FA** (autenticação de dois fatores)
2. **Rate Limiting** para tentativas de login
3. **Logs de Auditoria** para ações críticas
4. **Expiração de Senhas** periódica

### **Funcionalidades Adicionais**
1. **Recuperação de Senha** via email
2. **Verificação de Email** no registro
3. **Login Social** (Google, Facebook)
4. **Sessões Simultâneas** limitadas

### **Otimizações**
1. **Cache de Usuários** para performance
2. **JWT Tokens** para APIs
3. **OAuth 2.0** para integração externa
4. **Single Sign-On** (SSO)

---

**📅 Última Atualização:** Dezembro 2024  
**👨‍💻 Versão:** 1.0  
**🔧 Status:** ✅ Produção  
**�� Segurança:** Alto
