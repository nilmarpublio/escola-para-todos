from flask import Flask, render_template, redirect, url_for, flash, request, session, g, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Importar modelos e autenticação
from models_postgres import User
from auth import admin_required, professor_required, aluno_required, content_creator_required, user_management_required, analytics_required, guest_required

# Importar API e Swagger
from api.turmas import register_turmas_api
from api.swagger import create_swagger_blueprint, get_swagger_spec

# Carregar variáveis de ambiente
load_dotenv()

# Inicialização da aplicação
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configurações da aplicação
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '🔐 Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

# Configuração da API REST
api = Api(app, prefix='/api', decorators=[login_required])

# Configuração do Swagger
swagger_blueprint = create_swagger_blueprint()
app.register_blueprint(swagger_blueprint)

# Rota para especificação OpenAPI
@app.route('/static/swagger.json')
def swagger_spec():
    """Retorna a especificação OpenAPI"""
    return get_swagger_spec()

# Registrar endpoints da API
register_turmas_api(api)

@login_manager.user_loader
def load_user(user_id):
    """Carrega usuário para o Flask-Login"""
    db = get_db()
    return User.get_by_id(int(user_id), db)

def get_db():
    """Conectar ao banco de dados PostgreSQL"""
    if 'db' not in g:
        # Usar DATABASE_URL do Render ou configuração local
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            # Render usa DATABASE_URL
            g.db = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        else:
            # Configuração local
            g.db = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'escola_para_todos'),
                user=os.getenv('DB_USER', 'escola_user'),
                password=os.getenv('DB_PASSWORD', ''),
                cursor_factory=RealDictCursor
            )
    return g.db

def close_db(e=None):
    """Fechar conexão com o banco"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

app.teardown_appcontext(close_db)

# =====================================================
# ROTAS PÚBLICAS
# =====================================================

@app.route('/')
def splash():
    """Página inicial da aplicação"""
    return render_template('splash.html')

@app.route('/login', methods=['GET', 'POST'])
@guest_required
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if not username or not password:
            flash('❌ Por favor, preencha todos os campos.', 'error')
            return render_template('login.html')
        
        db = get_db()
        user = User.authenticate(username, password, db)
        
        if user:
            if not user.is_active:
                flash('❌ Sua conta foi desativada. Entre em contato com o administrador.', 'error')
                return render_template('login.html')
            
            login_user(user, remember=remember)
            flash(f'✅ Bem-vindo(a) de volta, {user.first_name}!', 'success')
            
            # Redirecionar baseado no tipo de usuário
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            elif user.is_professor:
                return redirect(url_for('professor_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('❌ Username ou senha incorretos.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
@guest_required
def register():
    """Página de registro"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        user_type = request.form.get('user_type', 'aluno')
        
        # Validações
        if not all([username, email, password, confirm_password, first_name, last_name]):
            flash('❌ Por favor, preencha todos os campos.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('❌ As senhas não coincidem.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('❌ A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('register.html')
        
        # Validar tipo de usuário (apenas alunos podem se registrar)
        if user_type != 'aluno':
            flash('❌ Apenas alunos podem se registrar. Professores e administradores são criados pelo admin.', 'error')
            return render_template('register.html')
        
        try:
            db = get_db()
            
            # Verificar se username já existe
            if User.get_by_username(username, db):
                flash('❌ Este username já está em uso.', 'error')
                return render_template('register.html')
            
            # Verificar se email já existe
            if User.get_by_email(email, db):
                flash('❌ Este email já está em uso.', 'error')
                return render_template('register.html')
            
            # Criar usuário
            user = User.create_user(username, email, password, first_name, last_name, user_type, db)
            
            flash('✅ Conta criada com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash(f'❌ Erro ao criar conta: {str(e)}', 'error')
    
    return render_template('register.html')

# =====================================================
# ROTAS AUTENTICADAS
# =====================================================

@app.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('👋 Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('splash'))

@app.route('/profile')
@login_required
def profile():
    """Perfil do usuário"""
    return render_template('profile.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Dashboard administrativo"""
    return render_template('admin_dashboard.html')

@app.route('/professor/dashboard')
@professor_required
def professor_dashboard():
    """Dashboard do professor"""
    return render_template('professor_dashboard.html')

@app.route('/student/dashboard')
@aluno_required
def student_dashboard():
    """Dashboard do estudante"""
    return render_template('student_dashboard.html')

@app.route('/health')
def health():
    """Health check para o Render"""
    return 'OK - Aplicação completa com PostgreSQL! 🚀', 200

@app.route('/version')
def version():
    """Verificar versão"""
    return 'app_postgres.py - Aplicação completa com PostgreSQL - Render Online! 🎯'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
