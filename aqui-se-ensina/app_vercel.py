#!/usr/bin/env python3
"""
Aqui se Aprende - Versão para Vercel + Supabase
"""

from flask import Flask, render_template, redirect, url_for, flash, request, session, g, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json

# Configurações para Vercel
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Importar Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    print("⚠️ Supabase não disponível")
    SUPABASE_AVAILABLE = False

# Importar modelos e autenticação
from models import User
from auth import admin_required, professor_required, aluno_required, content_creator_required, user_management_required, analytics_required, guest_required

# Importar API e Swagger
from api.turmas import register_turmas_api
from api.swagger import create_swagger_blueprint, get_swagger_spec

# Inicialização da aplicação
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'vercel-secret-key-change-in-production')

# Configurações da aplicação
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas
app.config['SESSION_COOKIE_SECURE'] = True  # True em produção
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Carregar usuário para o Flask-Login"""
    try:
        return User.get_by_id(int(user_id))
    except (ValueError, TypeError):
        return None

# Configuração da API REST
api = Api(app)

# Registrar blueprints da API
register_turmas_api(api)

# Configuração do Swagger
swagger_bp = create_swagger_blueprint()
app.register_blueprint(swagger_bp, url_prefix='/api/docs')

# Configuração do Supabase
def get_supabase_client():
    """Obter cliente Supabase"""
    if not SUPABASE_AVAILABLE:
        return None
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        return None
    
    return create_client(url, key)

# Rota de health check para Vercel
@app.route('/health')
def health_check():
    """Health check endpoint para Vercel"""
    try:
        supabase = get_supabase_client()
        
        if supabase:
            # Testar conexão com Supabase
            result = supabase.table('users').select('id').limit(1).execute()
            db_status = 'connected'
        else:
            db_status = 'not_configured'
        
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'platform': 'vercel',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Rota principal
@app.route('/')
def index():
    """Página inicial"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Rota de dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    return render_template('dashboard.html', user=current_user)

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('login.html')
        
        user = User.get_by_username(username)
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash(f'Bem-vindo, {user.nome}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos.', 'error')
    
    return render_template('login.html')

# Rota de logout
@app.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('index'))

# Rota de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        tipo_usuario = request.form.get('tipo_usuario', 'aluno')
        
        # Validações básicas
        if not all([nome, username, email, password, confirm_password]):
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('register.html')
        
        if User.get_by_username(username):
            flash('Nome de usuário já existe.', 'error')
            return render_template('register.html')
        
        if User.get_by_email(email):
            flash('Email já cadastrado.', 'error')
            return render_template('register.html')
        
        # Criar usuário
        try:
            user = User.create(
                nome=nome,
                username=username,
                email=email,
                password=password,
                tipo_usuario=tipo_usuario
            )
            
            flash('Conta criada com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            flash(f'Erro ao criar conta: {str(e)}', 'error')
    
    return render_template('register.html')

# Rota de perfil
@app.route('/profile')
@login_required
def profile():
    """Página de perfil do usuário"""
    return render_template('profile.html', user=current_user)

# Rota de administração
@app.route('/admin')
@admin_required
def admin():
    """Painel administrativo"""
    return render_template('admin.html', user=current_user)

# Rota de turmas
@app.route('/turmas')
@login_required
def turmas():
    """Lista de turmas"""
    return render_template('turmas.html', user=current_user)

# Rota de fórum
@app.route('/forum')
@login_required
def forum():
    """Fórum de discussões"""
    return render_template('forum.html', user=current_user)

# Rota de gamificação
@app.route('/gamificacao')
@login_required
def gamificacao():
    """Sistema de gamificação"""
    return render_template('gamificacao.html', user=current_user)

# Rota de relatórios
@app.route('/relatorios')
@login_required
def relatorios():
    """Relatórios e estatísticas"""
    return render_template('relatorios.html', user=current_user)

# Rota de configurações
@app.route('/configuracoes')
@login_required
def configuracoes():
    """Configurações da conta"""
    return render_template('configuracoes.html', user=current_user)

# Rota de ajuda
@app.route('/ajuda')
def ajuda():
    """Página de ajuda"""
    return render_template('ajuda.html')

# Rota de contato
@app.route('/contato')
def contato():
    """Página de contato"""
    return render_template('contato.html')

# Rota de sobre
@app.route('/sobre')
def sobre():
    """Página sobre o projeto"""
    return render_template('sobre.html')

# Rota de API - Swagger
@app.route('/api/docs')
def api_docs():
    """Documentação da API"""
    return render_template('swagger.html')

# Rota de API - Especificação OpenAPI
@app.route('/api/spec')
def api_spec():
    """Especificação OpenAPI"""
    return jsonify(get_swagger_spec())

# Rota de erro 404
@app.errorhandler(404)
def not_found(error):
    """Página de erro 404"""
    return render_template('404.html'), 404

# Rota de erro 500
@app.errorhandler(500)
def internal_error(error):
    """Página de erro 500"""
    return render_template('500.html'), 500

# Inicialização do banco de dados Supabase
def init_supabase():
    """Inicializar banco de dados Supabase"""
    try:
        supabase = get_supabase_client()
        
        if not supabase:
            print("⚠️ Supabase não configurado")
            return False
        
        # Verificar se a tabela users existe
        result = supabase.table('users').select('id').limit(1).execute()
        
        # Criar usuário admin padrão se não existir
        admin_result = supabase.table('users').select('id').eq('tipo_usuario', 'admin').execute()
        
        if not admin_result.data:
            admin_password = generate_password_hash('admin123')
            admin_user = {
                'nome': 'Administrador',
                'username': 'admin',
                'email': 'admin@aqui-se-aprende.com',
                'password_hash': admin_password,
                'tipo_usuario': 'admin',
                'ativo': True,
                'data_criacao': datetime.now().isoformat(),
                'data_atualizacao': datetime.now().isoformat()
            }
            
            supabase.table('users').insert(admin_user).execute()
            print("✅ Usuário admin criado no Supabase!")
        
        print("✅ Supabase inicializado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar Supabase: {e}")
        return False

# Inicializar Supabase na primeira execução
if __name__ == '__main__':
    print("🚀 Iniciando Aqui se Aprende - Versão Vercel")
    print("📊 Banco: Supabase (PostgreSQL)")
    print("🌐 Plataforma: Vercel")
    print("-" * 50)
    
    init_supabase()
    app.run(debug=True, host='0.0.0.0', port=5000)
