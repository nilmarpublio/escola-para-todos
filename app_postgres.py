from flask import Flask, render_template, redirect, url_for, flash, request, session, g, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import traceback
import sys

# Tratamento de erros de import
try:
    import psycopg
    from psycopg.rows import dict_row
    PSYCOPG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ psycopg não disponível: {e}")
    PSYCOPG_AVAILABLE = False

try:
    from models_postgres import User
    MODELS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ models_postgres não disponível: {e}")
    MODELS_AVAILABLE = False

try:
    from auth import admin_required, professor_required, aluno_required, content_creator_required, user_management_required, analytics_required, guest_required
    AUTH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ auth não disponível: {e}")
    AUTH_AVAILABLE = False

try:
    from api.turmas import register_turmas_api
    API_TURMAS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ api.turmas não disponível: {e}")
    API_TURMAS_AVAILABLE = False

try:
    from api.swagger import create_swagger_blueprint, get_swagger_spec
    SWAGGER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ api.swagger não disponível: {e}")
    SWAGGER_AVAILABLE = False

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv não disponível")

# Inicialização da aplicação
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configurações da aplicação
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configuração do Flask-Login (se disponível)
if AUTH_AVAILABLE:
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = '🔐 Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
else:
    print("⚠️ Flask-Login não configurado - auth não disponível")

# Configuração da API REST (se disponível)
if API_TURMAS_AVAILABLE:
    api = Api(app, prefix='/api')
    # Registrar endpoints da API
    register_turmas_api(api)
else:
    print("⚠️ API REST não configurada - api.turmas não disponível")

# Configuração do Swagger (se disponível)
if SWAGGER_AVAILABLE:
    swagger_blueprint = create_swagger_blueprint()
    app.register_blueprint(swagger_blueprint)
else:
    print("⚠️ Swagger não configurado - api.swagger não disponível")

# Funções auxiliares para os templates
@app.context_processor
def utility_processor():
    """Funções auxiliares disponíveis nos templates"""
    def get_user_type_display(user_type):
        """Converte o tipo de usuário para display"""
        user_types = {
            'admin': 'Administrador',
            'professor': 'Professor',
            'aluno': 'Aluno',
            'content_creator': 'Criador de Conteúdo',
            'user_management': 'Gestor de Usuários',
            'analytics': 'Analista',
            'guest': 'Visitante'
        }
        return user_types.get(user_type, user_type.title())
    
    return {
        'get_user_type_display': get_user_type_display
    }

# Rota para especificação OpenAPI
@app.route('/static/swagger.json')
def swagger_spec():
    """Retorna a especificação OpenAPI"""
    return get_swagger_spec()

# Registrar endpoints da API
# register_turmas_api(api) # Moved to above

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
            g.db = psycopg.connect(database_url, row_factory=dict_row)
        else:
            # Configuração local
            g.db = psycopg.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                dbname=os.getenv('DB_NAME', 'escola_para_todos'),
                user=os.getenv('DB_USER', 'escola_user'),
                password=os.getenv('DB_PASSWORD', ''),
                row_factory=dict_row
            )
    return g.db

def close_db(e=None):
    """Fechar conexão com o banco"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

app.teardown_appcontext(close_db)

# =====================================================
# ROTAS PROTEGIDAS - ALUNO
# =====================================================

@app.route('/student/dashboard')
@aluno_required
def student_dashboard():
    """Dashboard do aluno"""
    return render_template('student_dashboard.html')

@app.route('/student/turmas')
@aluno_required
def student_turmas():
    """Turmas do aluno"""
    return render_template('student_turmas.html')

@app.route('/student/aulas')
@aluno_required
def student_aulas():
    """Aulas do aluno"""
    return render_template('student_aulas.html')

@app.route('/student/aula/<int:aula_id>')
@aluno_required
def student_aula_view(aula_id):
    """Visualizar aula específica"""
    return render_template('student_aula_view.html', aula_id=aula_id)

@app.route('/student/exercicio/<int:exercicio_id>')
@aluno_required
def student_exercicio(exercicio_id):
    """Exercício do aluno"""
    return render_template('student_exercicio.html', exercicio_id=exercicio_id)

@app.route('/student/progresso')
@aluno_required
def student_progresso():
    """Progresso do aluno"""
    return render_template('student_progresso.html')

@app.route('/student/metas')
@aluno_required
def student_metas():
    """Metas do aluno"""
    return render_template('student_metas.html')

@app.route('/student/conquistas')
@aluno_required
def student_conquistas():
    """Conquistas do aluno"""
    return render_template('student_conquistas.html')

@app.route('/student/ranking')
@aluno_required
def student_ranking():
    """Ranking dos alunos"""
    return render_template('student_ranking.html')

@app.route('/student/gamificacao')
@aluno_required
def student_gamificacao():
    """Gamificação do aluno"""
    return render_template('student_gamificacao.html')

# =====================================================
# ROTAS PROTEGIDAS - PERFIL
# =====================================================

@app.route('/profile')
@login_required
def profile():
    """Perfil do usuário"""
    return render_template('profile.html')

@app.route('/profile/edit')
@login_required
def edit_profile():
    """Editar perfil"""
    return render_template('edit_profile.html')

@app.route('/change-password')
@login_required
def change_password():
    """Alterar senha"""
    return render_template('change_password.html')

# =====================================================
# ROTAS PÚBLICAS - FÓRUM
# =====================================================

@app.route('/forum')
def forum():
    """Fórum da comunidade"""
    return render_template('forum.html')

@app.route('/forum/topico/<int:topico_id>')
def forum_topico(topico_id):
    """Tópico específico do fórum"""
    return render_template('forum_topico.html', topico_id=topico_id)

@app.route('/forum/novo-topico')
@login_required
def forum_novo_topico():
    """Criar novo tópico"""
    return render_template('forum_novo_topico.html')

@app.route('/forum/busca')
def forum_busca():
    """Busca no fórum"""
    return render_template('forum_busca.html')

# =====================================================
# ROTAS PROTEGIDAS - LIÇÕES
# =====================================================

@app.route('/lesson/<int:lesson_id>')
@login_required
def lesson(lesson_id):
    """Lição específica"""
    return render_template('lesson.html', lesson_id=lesson_id)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
