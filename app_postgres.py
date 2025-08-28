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
    if not AUTH_AVAILABLE:
        return "Sistema de autenticação não disponível", 500
    
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            
            db = get_db()
            if not db:
                flash('❌ Erro de conexão com banco de dados', 'error')
                return render_template('login.html')
            
            # Usar o método authenticate que verifica a senha
            user = User.authenticate(username, password, db)
            
            if user:
                login_user(user)
                flash(f'🎉 Bem-vindo, {user.first_name}!', 'success')
                
                # Redirecionar baseado no tipo de usuário
                if user.is_admin:
                    return redirect(url_for('admin_dashboard'))
                elif user.is_professor:
                    return redirect(url_for('professor_dashboard'))
                else:
                    return redirect(url_for('student_dashboard'))
            else:
                flash('❌ Usuário ou senha incorretos!', 'error')
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            flash('❌ Erro interno no sistema', 'error')
    
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

@app.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('👋 Logout realizado com sucesso!', 'info')
    return redirect(url_for('splash'))

# =====================================================
# ROTAS PROTEGIDAS - ADMIN
# =====================================================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Dashboard administrativo"""
    return render_template('admin_dashboard.html')

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    """Gerenciamento de usuários"""
    return render_template('admin_usuarios.html')

@app.route('/admin/relatorios')
@admin_required
def admin_relatorios():
    """Relatórios administrativos"""
    return render_template('admin_relatorios.html')

@app.route('/admin/relatorio/usuarios')
@admin_required
def admin_relatorio_usuarios():
    """Relatório de usuários"""
    return render_template('admin_relatorio_usuarios.html')

@app.route('/admin/relatorio/turmas')
@admin_required
def admin_relatorio_turmas():
    """Relatório de turmas"""
    return render_template('admin_relatorio_turmas.html')

@app.route('/admin/criar/usuario')
@admin_required
def admin_criar_usuario():
    """Criar novo usuário"""
    return render_template('admin_criar_usuario.html')

@app.route('/admin/editar/usuario/<int:user_id>')
@admin_required
def admin_editar_usuario(user_id):
    """Editar usuário existente"""
    return render_template('admin_editar_usuario.html', user_id=user_id)

# =====================================================
# ROTAS PROTEGIDAS - PROFESSOR
# =====================================================

@app.route('/professor/dashboard')
@professor_required
def professor_dashboard():
    """Dashboard do professor"""
    return render_template('professor_dashboard.html')

@app.route('/professor/turmas')
@professor_required
def professor_turmas():
    """Turmas do professor"""
    return render_template('professor_turmas.html')

@app.route('/professor/aulas')
@professor_required
def professor_aulas():
    """Aulas do professor"""
    return render_template('professor_aulas.html')

@app.route('/professor/relatorios')
@professor_required
def professor_relatorios():
    """Relatórios do professor"""
    return render_template('professor_relatorios.html')

@app.route('/professor/relatorio/turma/<int:turma_id>')
@professor_required
def professor_relatorio_turma(turma_id):
    """Relatório de turma específica"""
    return render_template('professor_relatorio_turma.html', turma_id=turma_id)

@app.route('/professor/relatorio/aluno/<int:aluno_id>')
@professor_required
def professor_relatorio_aluno(aluno_id):
    """Relatório de aluno específico"""
    return render_template('professor_relatorio_aluno.html', aluno_id=aluno_id)

@app.route('/professor/criar/turma')
@professor_required
def professor_criar_turma():
    """Criar nova turma"""
    return render_template('professor_criar_turma.html')

@app.route('/professor/criar/aula')
@professor_required
def professor_criar_aula():
    """Criar nova aula"""
    return render_template('professor_criar_aula.html')

@app.route('/professor/editar/aula/<int:aula_id>')
@professor_required
def professor_editar_aula(aula_id):
    """Editar aula existente"""
    return render_template('professor_editar_aula.html', aula_id=aula_id)

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

@app.route('/forum/buscar')
def forum_buscar():
    """Busca no fórum (alias para forum_busca)"""
    return redirect(url_for('forum_busca'))

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
