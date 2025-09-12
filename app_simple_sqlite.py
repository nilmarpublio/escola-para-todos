from flask import Flask, render_template, redirect, url_for, flash, request, session, g, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import sqlite3

# Configurações locais (sem dotenv)
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'
os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Importar modelos e autenticação
from models import User
from auth import admin_required, professor_required, aluno_required, content_creator_required, user_management_required, analytics_required, guest_required

# Importar API e Swagger
from api.turmas import register_turmas_api
from api.swagger import create_swagger_blueprint, get_swagger_spec

# Inicialização da aplicação
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configurações da aplicação
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas
app.config['SESSION_COOKIE_SECURE'] = False  # False para desenvolvimento
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
register_turmas_api(api)

@login_manager.user_loader
def load_user(user_id):
    """Carrega usuário para o Flask-Login"""
    db = get_db()
    return User.get_by_id(int(user_id), db)

def get_db():
    """Conectar ao banco SQLite"""
    if 'db' not in g:
        g.db = sqlite3.connect('escola_para_todos.db')
        g.db.row_factory = sqlite3.Row
        g.db_type = 'sqlite'
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
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
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
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
@guest_required
def register():
    """Página de registro"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        user_type = request.form['user_type']
        
        db = get_db()
        
        # Verificar se usuário já existe
        if User.get_by_username(username, db):
            flash('❌ Usuário já existe!', 'error')
            return render_template('register.html')
        
        if User.get_by_email(email, db):
            flash('❌ Email já cadastrado!', 'error')
            return render_template('register.html')
        
        # Criar novo usuário
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type
        )
        user.set_password(password)
        
        if user.save(db):
            flash('✅ Usuário criado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('❌ Erro ao criar usuário!', 'error')
    
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
    # Versão simples sem estatísticas complexas
    return render_template('admin_dashboard.html', 
                         stats=[0, 0, 0, 0],  # Valores padrão
                         users=[],
                         recent_activities=[])

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

# =====================================================
# ROTAS PROTEGIDAS - LIÇÕES
# =====================================================

@app.route('/lesson/<int:lesson_id>')
@login_required
def lesson(lesson_id):
    """Lição específica"""
    return render_template('lesson.html', lesson_id=lesson_id)

# =====================================================
# ROTAS DE TESTE
# =====================================================

@app.route('/health')
def health():
    """Health check da aplicação"""
    db = get_db()
    db_type = getattr(g, 'db_type', 'unknown')
    
    return {
        'status': 'healthy',
        'database': db_type,
        'timestamp': datetime.now().isoformat(),
        'environment': os.getenv('FLASK_ENV', 'development')
    }

@app.route('/version')
def version():
    """Versão da aplicação"""
    return {
        'app': 'Escola para Todos',
        'version': '2.0.0',
        'database': 'SQLite (Local)',
        'environment': os.getenv('FLASK_ENV', 'development')
    }

@app.route('/test')
def test():
    """Página de teste"""
    return render_template('splash.html')

@app.route('/info')
def info():
    """Informações do sistema"""
    db = get_db()
    db_type = getattr(g, 'db_type', 'unknown')
    
    return {
        'database_type': db_type,
        'database_connected': db is not None,
        'environment': os.getenv('FLASK_ENV', 'development'),
        'debug_mode': os.getenv('FLASK_DEBUG', '0'),
        'secret_key_set': bool(os.getenv('SECRET_KEY')),
        'database_url_set': bool(os.getenv('DATABASE_URL'))
    }

if __name__ == '__main__':
    # Verificar se o banco SQLite existe, se não, criar
    if not os.path.exists('escola_para_todos.db'):
        print("🗄️ Banco SQLite não encontrado. Criando...")
        import init_db
        init_db.init_database()
        print("✅ Banco SQLite criado com sucesso!")
    
    print("🚀 Iniciando Escola para Todos (SQLite)")
    print("📊 Banco: SQLite local")
    print("🌍 Ambiente:", os.getenv('FLASK_ENV', 'development'))
    
    app.run(debug=True, host='0.0.0.0', port=5000)
