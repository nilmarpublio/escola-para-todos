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
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres'),
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
            
            print(f"🔍 DEBUG: Tentativa de login - Username: '{username}', Senha: '{password[:3]}...'")
            
            db = get_db()
            if not db:
                print("❌ DEBUG: Falha na conexão com banco de dados")
                flash('❌ Erro de conexão com banco de dados', 'error')
                return render_template('login.html')
            
            print("✅ DEBUG: Conexão com banco estabelecida")
            
            # Usar o método authenticate que verifica a senha
            print(f"🔐 DEBUG: Chamando User.authenticate('{username}', '***', db)")
            user = User.authenticate(username, password, db)
            
            if user:
                print(f"✅ DEBUG: Usuário autenticado com sucesso: {user.username} ({user.user_type})")
                login_user(user)
                flash(f'🎉 Bem-vindo, {user.first_name}!', 'success')
                
                # Redirecionar baseado no tipo de usuário
                if user.is_admin:
                    print("🔄 DEBUG: Redirecionando para admin_dashboard")
                    return redirect(url_for('admin_dashboard'))
                elif user.is_professor:
                    print("🔄 DEBUG: Redirecionando para professor_dashboard")
                    return redirect(url_for('professor_dashboard'))
                else:
                    print("🔄 DEBUG: Redirecionando para student_dashboard")
                    return redirect(url_for('student_dashboard'))
            else:
                print(f"❌ DEBUG: Falha na autenticação para username: '{username}'")
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
    try:
        db = get_db()
        
        # Estatísticas básicas
        cur = db.cursor()
        
        # Contar usuários por tipo
        cur.execute('SELECT user_type, COUNT(*) FROM users GROUP BY user_type')
        user_stats_raw = cur.fetchall()
        user_stats = {row['user_type']: row['count'] for row in user_stats_raw}
        
        # Contar turmas
        cur.execute('SELECT COUNT(*) FROM turmas')
        turmas_count = cur.fetchone()['count']
        
        # Contar aulas
        cur.execute('SELECT COUNT(*) FROM aulas')
        aulas_count = cur.fetchone()['count']
        
        # Contar matrículas
        cur.execute('SELECT COUNT(*) FROM matriculas')
        matriculas_count = cur.fetchone()['count']
        
        # Contar exercícios
        cur.execute('SELECT COUNT(*) FROM exercicios')
        exercicios_count = cur.fetchone()['count']
        
        cur.close()
        
        # Preparar dados para o template
        stats = {
            'total_users': sum(user_stats.values()),
            'admin_users': user_stats.get('admin', 0),
            'professor_users': user_stats.get('professor', 0),
            'aluno_users': user_stats.get('aluno', 0),
            'total_turmas': turmas_count,
            'total_aulas': aulas_count,
            'total_matriculas': matriculas_count,
            'total_exercicios': exercicios_count
        }
        
        return render_template('admin_dashboard.html', stats=stats)
        
    except Exception as e:
        print(f"❌ Erro no dashboard admin: {e}")
        # Retornar com estatísticas vazias em caso de erro
        stats = {
            'total_users': 0,
            'admin_users': 0,
            'professor_users': 0,
            'aluno_users': 0,
            'total_turmas': 0,
            'total_aulas': 0,
            'total_matriculas': 0,
            'total_exercicios': 0
        }
        return render_template('admin_dashboard.html', stats=stats)

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
    try:
        db = get_db()
        cur = db.cursor()
        
        # Estatísticas do professor
        professor_id = current_user.id
        
        # Contar aulas do professor
        cur.execute('SELECT COUNT(*) FROM aulas WHERE professor_id = %s', (professor_id,))
        total_aulas = cur.fetchone()['count']
        
        # Contar turmas do professor
        cur.execute('SELECT COUNT(*) FROM turmas WHERE professor_id = %s', (professor_id,))
        total_turmas = cur.fetchone()['count']
        
        # Contar alunos matriculados nas turmas do professor
        cur.execute('''
            SELECT COUNT(DISTINCT m.aluno_id) 
            FROM matriculas m 
            JOIN turmas t ON m.turma_id = t.id 
            WHERE t.professor_id = %s
        ''', (professor_id,))
        total_alunos = cur.fetchone()['count']
        
        # Contar exercícios do professor
        cur.execute('''
            SELECT COUNT(*) 
            FROM exercicios e 
            JOIN aulas a ON e.aula_id = a.id 
            WHERE a.professor_id = %s
        ''', (professor_id,))
        total_exercicios = cur.fetchone()['count']
        
        cur.close()
        
        # Buscar aulas do professor
        cur.execute('''
            SELECT id, titulo, disciplina, serie, created_at 
            FROM aulas 
            WHERE professor_id = %s 
            ORDER BY created_at DESC 
            LIMIT 5
        ''', (professor_id,))
        aulas = cur.fetchall()
        
        # Buscar turmas do professor
        cur.execute('''
            SELECT id, nome, serie, created_at 
            FROM turmas 
            WHERE professor_id = %s 
            ORDER BY created_at DESC 
            LIMIT 5
        ''', (professor_id,))
        turmas = cur.fetchall()
        
        cur.close()
        
        # Dados para o template
        data = {
            'total_aulas': total_aulas,
            'total_turmas': total_turmas,
            'total_alunos': total_alunos,
            'total_exercicios': total_exercicios,
            'aulas': aulas,
            'turmas': turmas
        }
        
        return render_template('professor_dashboard.html', data=data)
        
    except Exception as e:
        print(f"❌ Erro no dashboard professor: {e}")
        # Retornar com dados vazios em caso de erro
        data = {
            'total_aulas': 0,
            'total_turmas': 0,
            'total_alunos': 0,
            'total_exercicios': 0,
            'aulas': [],
            'turmas': []
        }
        return render_template('professor_dashboard.html', data=data)

@app.route('/professor/turmas')
@professor_required
def professor_turmas():
    """Turmas do professor"""
    try:
        db = get_db()
        cur = db.cursor()
        
        # Buscar turmas do professor
        professor_id = current_user.id
        cur.execute('''
            SELECT t.id, t.nome, t.serie, t.created_at,
                   COALESCE(COUNT(m.aluno_id), 0) as total_alunos
            FROM turmas t
            LEFT JOIN matriculas m ON t.id = m.turma_id
            WHERE t.professor_id = %s 
            GROUP BY t.id, t.nome, t.serie, t.created_at
            ORDER BY t.created_at DESC
        ''', (professor_id,))
        turmas = cur.fetchall()
        
        cur.close()
        
        return render_template('professor_turmas.html', turmas=turmas)
        
    except Exception as e:
        print(f"❌ Erro ao buscar turmas do professor: {e}")
        return render_template('professor_turmas.html', turmas=[])

@app.route('/professor/aulas')
@professor_required
def professor_aulas():
    """Aulas do professor"""
    try:
        db = get_db()
        cur = db.cursor()
        
        # Buscar aulas do professor
        professor_id = current_user.id
        cur.execute('''
            SELECT id, titulo, disciplina, serie, created_at, descricao, duracao_minutos
            FROM aulas 
            WHERE professor_id = %s 
            ORDER BY created_at DESC
        ''', (professor_id,))
        aulas = cur.fetchall()
        
        cur.close()
        
        return render_template('professor_aulas.html', aulas=aulas)
        
    except Exception as e:
        print(f"❌ Erro ao buscar aulas do professor: {e}")
        return render_template('professor_aulas.html', aulas=[])

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
    try:
        db = get_db()
        cur = db.cursor()
        
        # Estatísticas do aluno
        aluno_id = current_user.id
        
        # Contar aulas iniciadas
        cur.execute('''
            SELECT COUNT(*) 
            FROM progresso_alunos 
            WHERE aluno_id = %s AND status IN ('iniciada', 'em_progresso')
        ''', (aluno_id,))
        aulas_iniciadas = cur.fetchone()['count']
        
        # Contar aulas concluídas
        cur.execute('''
            SELECT COUNT(*) 
            FROM progresso_alunos 
            WHERE aluno_id = %s AND status = 'concluida'
        ''', (aluno_id,))
        aulas_concluidas = cur.fetchone()['count']
        
        # Contar pontos ganhos
        cur.execute('''
            SELECT COALESCE(SUM(pontos_ganhos), 0) 
            FROM respostas_alunos 
            WHERE aluno_id = %s
        ''', (aluno_id,))
        pontos_ganhos = cur.fetchone()['coalesce']
        
        # Calcular nível atual (baseado nos pontos)
        nivel_atual = max(1, pontos_ganhos // 100)  # 1 nível a cada 100 pontos
        
        cur.close()
        
        # Dados para o template
        data = {
            'aulas_iniciadas': aulas_iniciadas,
            'aulas_concluidas': aulas_concluidas,
            'pontos_ganhos': pontos_ganhos,
            'nivel_atual': nivel_atual
        }
        
        return render_template('student_dashboard.html', data=data)
        
    except Exception as e:
        print(f"❌ Erro no dashboard aluno: {e}")
        # Retornar com dados vazios em caso de erro
        data = {
            'aulas_iniciadas': 0,
            'aulas_concluidas': 0,
            'pontos_ganhos': 0,
            'nivel_atual': 1
        }
        return render_template('student_dashboard.html', data=data)

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
    try:
        db = get_db()
        cur = db.cursor()
        
        # Buscar dados de progresso do aluno
        aluno_id = current_user.id
        
        # Total de aulas
        cur.execute('''
            SELECT COUNT(DISTINCT a.id) as total_aulas
            FROM aulas a
            JOIN matriculas m ON a.turma_id = m.turma_id
            WHERE m.aluno_id = %s
        ''', (aluno_id,))
        total_aulas = cur.fetchone()['total_aulas'] if cur.fetchone() else 0
        
        # Aulas concluídas
        cur.execute('''
            SELECT COUNT(DISTINCT a.id) as aulas_concluidas
            FROM aulas a
            JOIN progresso_alunos pa ON a.id = pa.aula_id
            WHERE pa.aluno_id = %s AND pa.status = 'concluida'
        ''', (aluno_id,))
        aulas_concluidas = cur.fetchone()['aulas_concluidas'] if cur.fetchone() else 0
        
        # Total de pontos
        cur.execute('''
            SELECT COALESCE(SUM(ra.pontos_ganhos), 0) as total_pontos
            FROM respostas_alunos ra
            WHERE ra.aluno_id = %s
        ''', (aluno_id,))
        total_pontos = cur.fetchone()['total_pontos'] if cur.fetchone() else 0
        
        # Tempo total de estudo (em minutos)
        cur.execute('''
            SELECT COALESCE(SUM(pa.tempo_gasto), 0) as tempo_total
            FROM progresso_alunos pa
            WHERE pa.aluno_id = %s
        ''', (aluno_id,))
        tempo_total = cur.fetchone()['tempo_total'] if cur.fetchone() else 0
        
        # Progresso por disciplina
        cur.execute('''
            SELECT 
                a.disciplina,
                COUNT(DISTINCT a.id) as total_aulas,
                COUNT(DISTINCT CASE WHEN pa.status = 'concluida' THEN a.id END) as aulas_concluidas
            FROM aulas a
            JOIN matriculas m ON a.turma_id = m.turma_id
            LEFT JOIN progresso_alunos pa ON a.id = pa.aula_id AND pa.aluno_id = %s
            WHERE m.aluno_id = %s
            GROUP BY a.disciplina
        ''', (aluno_id, aluno_id))
        progresso_disciplina = {}
        for row in cur.fetchall():
            progresso_disciplina[row['disciplina']] = {
                'total': row['total_aulas'],
                'concluidas': row['aulas_concluidas'],
                'percentual': (row['aulas_concluidas'] / row['total_aulas'] * 100) if row['total_aulas'] > 0 else 0
            }
        
        # Progresso por série
        cur.execute('''
            SELECT 
                a.serie,
                COUNT(DISTINCT a.id) as total_aulas,
                COUNT(DISTINCT CASE WHEN pa.status = 'concluida' THEN a.id END) as aulas_concluidas
            FROM aulas a
            JOIN matriculas m ON a.turma_id = m.turma_id
            LEFT JOIN progresso_alunos pa ON a.id = pa.aula_id AND pa.aluno_id = %s
            WHERE m.aluno_id = %s
            GROUP BY a.serie
        ''', (aluno_id, aluno_id))
        progresso_serie = {}
        for row in cur.fetchall():
            progresso_serie[row['serie']] = {
                'total': row['total_aulas'],
                'concluidas': row['aulas_concluidas'],
                'percentual': (row['aulas_concluidas'] / row['total_aulas'] * 100) if row['total_aulas'] > 0 else 0
            }
        
        # Aulas em progresso
        cur.execute('''
            SELECT 
                a.id, a.titulo, a.disciplina, a.serie,
                pa.status, pa.tempo_gasto, pa.ultimo_acesso
            FROM aulas a
            JOIN progresso_alunos pa ON a.id = pa.aula_id
            WHERE pa.aluno_id = %s AND pa.status IN ('iniciada', 'em_progresso')
            ORDER BY pa.ultimo_acesso DESC
        ''', (aluno_id,))
        aulas_progresso = cur.fetchall()
        
        cur.close()
        
        # Dados para o template
        data = {
            'total_aulas': total_aulas,
            'aulas_concluidas': aulas_concluidas,
            'total_pontos': total_pontos,
            'tempo_total': tempo_total,
            'progresso_disciplina': progresso_disciplina,
            'progresso_serie': progresso_serie,
            'aulas_progresso': aulas_progresso
        }
        
        return render_template('student_progresso.html', data=data)
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados de progresso: {e}")
        # Retornar com dados vazios em caso de erro
        data = {
            'total_aulas': 0,
            'aulas_concluidas': 0,
            'total_pontos': 0,
            'tempo_total': 0,
            'progresso_disciplina': {},
            'progresso_serie': {},
            'aulas_progresso': []
        }
        return render_template('student_progresso.html', data=data)

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
    try:
        db = get_db()
        cur = db.cursor()
        
        # Buscar dados de gamificação do aluno
        aluno_id = current_user.id
        cur.execute('''
            SELECT 
                COALESCE(SUM(pontos), 0) as total_pontos,
                COALESCE(COUNT(DISTINCT conquista_id), 0) as total_conquistas,
                COALESCE(MAX(nivel), 1) as nivel_atual
            FROM (
                SELECT 
                    COALESCE(SUM(ex.pontos), 0) as pontos,
                    NULL as conquista_id,
                    NULL as nivel
                FROM exercicios ex
                JOIN respostas_alunos ra ON ex.id = ra.exercicio_id
                WHERE ra.aluno_id = %s
                
                UNION ALL
                
                SELECT 
                    0 as pontos,
                    c.id as conquista_id,
                    c.nivel_requerido as nivel
                FROM conquistas c
                JOIN conquistas_alunos ca ON c.id = ca.conquista_id
                WHERE ca.aluno_id = %s
            ) gamificacao
        ''', (aluno_id, aluno_id))
        
        result = cur.fetchone()
        total_pontos = result[0] if result else 0
        total_conquistas = result[1] if result else 0
        nivel_atual = result[2] if result else 1
        
        cur.close()
        
        # Buscar informações adicionais
        # Aulas concluídas
        cur.execute('''
            SELECT COUNT(DISTINCT a.id) as aulas_concluidas
            FROM aulas a
            JOIN progresso_alunos pa ON a.id = pa.aula_id
            WHERE pa.aluno_id = %s AND pa.status = 'concluida'
        ''', (aluno_id,))
        aulas_concluidas = cur.fetchone()[0] if cur.fetchone() else 0
        
        # Conquistas
        cur.execute('''
            SELECT COUNT(*) as conquistas_count
            FROM conquistas_alunos
            WHERE aluno_id = %s
        ''', (aluno_id,))
        conquistas_count = cur.fetchone()[0] if cur.fetchone() else 0
        
        # Ranking
        cur.execute('''
            SELECT 
                COUNT(*) as total_alunos,
                (SELECT COUNT(*) + 1 
                 FROM (
                     SELECT COALESCE(SUM(pontos), 0) as total_pontos
                     FROM exercicios ex
                     JOIN respostas_alunos ra ON ex.id = ra.exercicio_id
                     GROUP BY ra.aluno_id
                 ) ranking
                 WHERE total_pontos > %s
                ) as posicao_ranking
            FROM users
            WHERE user_type = 'aluno'
        ''', (total_pontos,))
        ranking_result = cur.fetchone()
        total_alunos = ranking_result[0] if ranking_result else 0
        posicao_ranking = ranking_result[1] if ranking_result else 1
        
        # Informações do nível
        nivel_info = {
            1: {'nome': 'Iniciante', 'cor': '#28a745', 'min_pontos': 0, 'max_pontos': 100},
            2: {'nome': 'Aprendiz', 'cor': '#17a2b8', 'min_pontos': 101, 'max_pontos': 300},
            3: {'nome': 'Intermediário', 'cor': '#ffc107', 'min_pontos': 301, 'max_pontos': 600},
            4: {'nome': 'Avançado', 'cor': '#fd7e14', 'min_pontos': 601, 'max_pontos': 1000},
            5: {'nome': 'Mestre', 'cor': '#dc3545', 'min_pontos': 1001, 'max_pontos': 9999}
        }
        
        # Calcular progresso do nível atual
        nivel_atual_info = nivel_info.get(nivel_atual, nivel_info[1])
        pontos_nivel_atual = total_pontos - nivel_atual_info['min_pontos']
        pontos_necessarios = nivel_atual_info['max_pontos'] - nivel_atual_info['min_pontos']
        progresso_nivel = min(100, max(0, (pontos_nivel_atual / pontos_necessarios) * 100)) if pontos_necessarios > 0 else 100
        
        cur.close()
        
        return render_template('student_gamificacao.html', 
                             total_pontos=total_pontos,
                             total_conquistas=total_conquistas,
                             nivel_atual=nivel_atual,
                             aulas_concluidas=aulas_concluidas,
                             conquistas_count=conquistas_count,
                             posicao_ranking=posicao_ranking,
                             total_alunos=total_alunos,
                             nivel_info=nivel_info,
                             progresso_nivel=progresso_nivel)
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados de gamificação: {e}")
        return render_template('student_gamificacao.html',
                             total_pontos=0,
                             total_conquistas=0,
                             nivel_atual=1,
                             aulas_concluidas=0,
                             conquistas_count=0,
                             posicao_ranking=1,
                             total_alunos=0,
                             nivel_info={1: {'nome': 'Iniciante', 'cor': '#28a745', 'min_pontos': 0, 'max_pontos': 100}},
                             progresso_nivel=0)

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
    app.run(host='0.0.0.0', port=port, debug=True)
