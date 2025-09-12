#!/usr/bin/env python3
"""
Versão local do Aqui se Aprende com SQLite
Para testar enquanto o Fly.io resolve os problemas de rede
"""

from flask import Flask, render_template, redirect, url_for, flash, request, session, g, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import sqlite3

# Configurações locais
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'
os.environ['SECRET_KEY'] = 'local-dev-secret-key'

# Importar modelos e autenticação
from models import User
from auth import admin_required, professor_required, aluno_required, content_creator_required, user_management_required, analytics_required, guest_required

# Importar API e Swagger
from api.turmas import register_turmas_api
from api.swagger import create_swagger_blueprint, get_swagger_spec

# Inicialização da aplicação
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'local-dev-secret-key')

# Configurações da aplicação
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas
app.config['SESSION_COOKIE_SECURE'] = False  # False para desenvolvimento local
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

# Rota de health check
@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Testar conexão com banco
        conn = sqlite3.connect('educa_facil_local.db')
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat(),
            'version': 'local-sqlite'
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

# Inicialização do banco de dados
def init_db():
    """Inicializar banco de dados SQLite local"""
    try:
        conn = sqlite3.connect('educa_facil_local.db')
        cursor = conn.cursor()
        
        # Criar tabelas se não existirem
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                tipo_usuario TEXT NOT NULL DEFAULT 'aluno',
                ativo BOOLEAN NOT NULL DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar usuário admin padrão se não existir
        cursor.execute('SELECT COUNT(*) FROM users WHERE tipo_usuario = "admin"')
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            admin_password = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO users (nome, username, email, password_hash, tipo_usuario)
                VALUES (?, ?, ?, ?, ?)
            ''', ('Administrador', 'admin', 'admin@educafacil.com', admin_password, 'admin'))
        
        conn.commit()
        conn.close()
        
        print("✅ Banco de dados SQLite local inicializado com sucesso!")
        print(" Usuário admin criado: admin / admin123")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")

# Inicializar banco na primeira execução
if __name__ == '__main__':
    print("🚀 Iniciando Aqui se Aprende - Versão Local")
    print("📁 Banco de dados: educa_facil_local.db")
    print("🌐 Acesse: http://localhost:5000")
    print("👤 Admin: admin / admin123")
    print("-" * 50)
    
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
