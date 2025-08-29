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

def create_default_users():
    """Cria usuários padrão se não existirem"""
    try:
        db = get_db()
        if not db:
            print("⚠️ Não foi possível conectar ao banco para criar usuários padrão")
            return
        
        cur = db.cursor()
        
        # Verificar se já existem usuários
        cur.execute("SELECT COUNT(*) as count FROM users")
        user_count = cur.fetchone()['count']
        
        if user_count > 1:  # Se já tem mais de 1 usuário, não precisa criar
            print(f"✅ Usuários já existem no banco ({user_count} usuários)")
            cur.close()
            return
        
        print("🔧 Criando usuários padrão...")
        
        # Usuários padrão
        default_users = [
            ('admin', 'admin123', 'admin', 'Admin', 'Sistema', 'admin@escola.com'),
            ('prof.matematica', 'prof123', 'professor', 'João', 'Silva', 'joao.silva@escola.com'),
            ('prof.portugues', 'prof123', 'professor', 'Maria', 'Santos', 'maria.santos@escola.com'),
            ('aluno.joao', 'aluno123', 'aluno', 'João', 'Pereira', 'joao.pereira@escola.com'),
            ('aluno.ana', 'aluno123', 'aluno', 'Ana', 'Costa', 'ana.costa@escola.com'),
            ('aluno.pedro', 'aluno123', 'aluno', 'Pedro', 'Oliveira', 'pedro.oliveira@escola.com'),
        ]
        
        for username, password, user_type, first_name, last_name, email in default_users:
            # Verificar se o usuário já existe
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            existing_user = cur.fetchone()
            
            if not existing_user:
                # Criar novo usuário
                from werkzeug.security import generate_password_hash
                hashed_password = generate_password_hash(password)
                
                cur.execute("""
                    INSERT INTO users (username, password_hash, user_type, first_name, last_name, email, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, true)
                """, (username, hashed_password, user_type, first_name, last_name, email))
                print(f"   ✅ Criado: {username} ({user_type})")
            else:
                print(f"   🔄 Já existe: {username}")
        
        db.commit()
        cur.close()
        print("🎉 Usuários padrão criados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuários padrão: {e}")
        import traceback
        traceback.print_exc()

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
        try:
            # Usar DATABASE_URL do Render ou configuração local
            database_url = os.getenv('DATABASE_URL')
            if database_url:
                # Render usa DATABASE_URL
                g.db = psycopg.connect(database_url, row_factory=dict_row)
                print("✅ Conectado ao PostgreSQL (Render)")
            else:
                # Configuração local
                g.db = psycopg.connect(
                    host=os.getenv('DB_HOST', 'localhost'),
                    dbname=os.getenv('DB_NAME', 'escola_para_todos'),
                    user=os.getenv('DB_USER', 'postgres'),
                    password=os.getenv('DB_PASSWORD', 'postgres'),
                    row_factory=dict_row
                )
                print("✅ Conectado ao PostgreSQL (local)")
        except Exception as e:
            print(f"❌ Erro ao conectar ao banco: {e}")
            g.db = None
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
    print("🔍 DEBUG: Rota splash chamada")
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

@app.route('/admin/criar/usuario', methods=['GET', 'POST'])
@admin_required
def admin_criar_usuario():
    """Criar novo usuário"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        if not all([username, email, password, user_type]):
            flash('Todos os campos são obrigatórios', 'error')
            return render_template('admin_criar_usuario.html')
        
        db = get_db()
        if not db:
            flash('Erro de conexão com o banco de dados', 'error')
            return render_template('admin_criar_usuario.html')
        
        try:
            # Verificar se usuário já existe
            cur = db.cursor()
            cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            existing_user = cur.fetchone()
            
            if existing_user:
                flash('Usuário ou email já existe', 'error')
                cur.close()
                return render_template('admin_criar_usuario.html')
            
            # Criar hash da senha
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash(password)
            
            # Inserir novo usuário
            cur.execute("""
                INSERT INTO users (username, email, password_hash, user_type, first_name, last_name, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, true, NOW(), NOW())
            """, (username, email, password_hash, user_type, first_name, last_name))
            
            db.commit()
            cur.close()
            
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            flash(f'Erro ao criar usuário: {e}', 'error')
            db.rollback()
            cur.close()
    
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
@login_required
@aluno_required
def student_dashboard():
    """Dashboard do aluno"""
    try:
        print(f"🔍 DEBUG: Iniciando student_dashboard para usuário {current_user.id} ({current_user.user_type})")
        
        db = get_db()
        cur = db.cursor()
        
        # Estatísticas básicas - simplificadas
        try:
            cur.execute("""
                SELECT COUNT(*) as total_aulas
                FROM aulas a
                JOIN matriculas m ON a.turma_id = m.turma_id
                WHERE m.aluno_id = %s AND m.status = 'ativa' AND a.is_active = true
            """, (current_user.id,))
            total_aulas = cur.fetchone()['total_aulas']
        except:
            total_aulas = 0
        
        # Aulas em progresso - simplificadas
        try:
            cur.execute("""
                SELECT COUNT(*) as aulas_em_progresso
                FROM progresso_alunos
                WHERE aluno_id = %s AND status = 'em_progresso'
            """, (current_user.id,))
            aulas_em_progresso = cur.fetchone()['aulas_em_progresso']
        except:
            aulas_em_progresso = 0
        
        # Aulas concluídas - simplificadas
        try:
            cur.execute("""
                SELECT COUNT(*) as aulas_concluidas
                FROM progresso_alunos
                WHERE aluno_id = %s AND status = 'concluida'
            """, (current_user.id,))
            aulas_concluidas = cur.fetchone()['aulas_concluidas']
        except:
            aulas_concluidas = 0
        
        # Total de pontos - simplificadas
        try:
            cur.execute("""
                SELECT COALESCE(SUM(e.pontos), 0) as total_pontos
                FROM progresso_alunos pa
                JOIN aulas a ON pa.aula_id = a.id
                JOIN exercicios e ON a.id = e.aula_id
                WHERE pa.aluno_id = %s AND pa.status = 'concluida'
            """, (current_user.id,))
            total_pontos = cur.fetchone()['total_pontos']
        except:
            total_pontos = 0
        
        # Nível atual (baseado em pontos)
        nivel_atual = (total_pontos // 100) + 1
        
        # Aulas disponíveis - simplificadas
        try:
            cur.execute("""
                SELECT a.id, a.titulo, a.descricao, a.duracao_minutos, 
                       t.nome as turma_nome, COALESCE(pa.status, 'não iniciada') as progresso_status
                FROM aulas a
                JOIN turmas t ON a.turma_id = t.id
                JOIN matriculas m ON t.id = m.turma_id
                LEFT JOIN progresso_alunos pa ON a.id = pa.aula_id AND pa.aluno_id = %s
                WHERE m.aluno_id = %s AND m.status = 'ativa' AND a.is_active = true
                ORDER BY a.titulo
            """, (current_user.id, current_user.id))
            aulas_disponiveis = cur.fetchall()
        except:
            aulas_disponiveis = []
        
        # Turmas matriculadas - simplificadas
        try:
            cur.execute("""
                SELECT t.id, t.nome, t.descricao
                FROM turmas t
                JOIN matriculas m ON t.id = m.turma_id
                WHERE m.aluno_id = %s AND m.status = 'ativa'
            """, (current_user.id,))
            turmas_matriculadas = cur.fetchall()
        except:
            turmas_matriculadas = []
        
        cur.close()
        
        data = {
            'total_aulas': total_aulas,
            'aulas_em_progresso': aulas_em_progresso,
            'aulas_concluidas': aulas_concluidas,
            'total_pontos': total_pontos,
            'nivel_atual': nivel_atual,
            'aulas_disponiveis': aulas_disponiveis,
            'turmas_matriculadas': turmas_matriculadas
        }
        
        print(f"✅ DEBUG: Dashboard carregado com sucesso, renderizando template")
        return render_template('student_dashboard.html', data=data)
        
    except Exception as e:
        print(f"❌ Erro no dashboard do aluno: {e}")
        import traceback
        traceback.print_exc()
        
        # Retornar dados vazios em caso de erro
        data = {
            'total_aulas': 0,
            'aulas_em_progresso': 0,
            'aulas_concluidas': 0,
            'total_pontos': 0,
            'nivel_atual': 1,
            'aulas_disponiveis': [],
            'turmas_matriculadas': []
        }
        
        flash('⚠️ Dashboard carregado com dados limitados devido a um erro.', 'warning')
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

@app.route('/aula/<int:aula_id>')
@login_required
def ver_aula(aula_id):
    """Visualizar uma aula específica"""
    try:
        db = get_db()
        cur = db.cursor()
        
        # Buscar dados da aula
        cur.execute("""
            SELECT a.*, t.nome as turma_nome, u.first_name, u.last_name
            FROM aulas a
            LEFT JOIN turmas t ON a.turma_id = t.id
            LEFT JOIN users u ON a.professor_id = u.id
            WHERE a.id = %s AND a.is_active = true
        """, (aula_id,))
        
        aula = cur.fetchone()
        if not aula:
            flash('❌ Aula não encontrada!', 'error')
            return redirect(url_for('student_dashboard'))
        
        # Buscar exercícios da aula
        cur.execute("""
            SELECT id, titulo, pergunta, opcoes, resposta_correta, tipo, pontos
            FROM exercicios
            WHERE aula_id = %s AND is_active = true
            ORDER BY id
        """, (aula_id,))
        
        exercicios = cur.fetchall()
        
        # Buscar progresso do aluno
        cur.execute("""
            SELECT status, data_inicio, data_conclusao, tempo_gasto
            FROM progresso_alunos
            WHERE aluno_id = %s AND aula_id = %s
        """, (current_user.id, aula_id))
        
        progresso_raw = cur.fetchone()
        
        # Calcular percentual de progresso
        if progresso_raw:
            if progresso_raw['status'] == 'concluida':
                percentual = 100
            elif progresso_raw['status'] == 'em_progresso':
                percentual = 50
            else:
                percentual = 25
        else:
            percentual = 0
            
        progresso = {
            'status': progresso_raw['status'] if progresso_raw else 'não iniciada',
            'percentual': percentual,
            'tempo_gasto': progresso_raw['tempo_gasto'] if progresso_raw and progresso_raw['tempo_gasto'] else 0
        }
        
        # Buscar próximas aulas da mesma turma
        cur.execute("""
            SELECT id, titulo, disciplina, duracao_minutos
            FROM aulas
            WHERE turma_id = %s AND ordem > %s AND is_active = true
            ORDER BY ordem
            LIMIT 5
        """, (aula.turma_id, aula.ordem or 0))
        
        proximas_aulas = cur.fetchall()
        
        # Calcular total de pontos dos exercícios
        total_pontos = sum(ex['pontos'] for ex in exercicios)
        
        cur.close()
        
        return render_template('lesson.html', 
                             aula=aula, 
                             exercicios=exercicios, 
                             progresso=progresso,
                             proximas_aulas=proximas_aulas,
                             total_pontos=total_pontos)
                             
    except Exception as e:
        print(f"Erro ao carregar aula: {e}")
        flash('❌ Erro ao carregar a aula!', 'error')
        return redirect(url_for('student_dashboard'))

# Rota para educação infantil (0-5 anos)
@app.route('/kids/dashboard')
@app.route('/student/educacao-basica')
@login_required
@aluno_required
def kids_dashboard():
    """Dashboard para educação infantil (0-5 anos)"""
    try:
        print(f"🔍 DEBUG: kids_dashboard chamado para usuário {current_user.id}")
        
        db = get_db()
        cur = db.cursor()
        
        # Buscar aulas específicas para educação infantil
        print("🔍 Executando query para kids_dashboard...")
        try:
            # Query corrigida para usar as colunas que realmente existem
            cur.execute("""
                SELECT a.id, a.titulo, a.descricao, 
                       30 as duracao_minutos, 
                       t.nome as turma_nome, t.descricao as turma_descricao
                FROM aulas a
                LEFT JOIN turmas t ON a.turma_id = t.id
                WHERE a.is_active = true 
                AND (t.nome ILIKE '%infantil%' OR t.nome ILIKE '%pré%' OR t.nome ILIKE '%pre%' OR t.nome ILIKE '%básico%')
                ORDER BY a.id
            """)
            print("✅ Query executada com sucesso!")
            aulas_infantil = cur.fetchall()
        except Exception as query_error:
            print(f"❌ Erro na query: {query_error}")
            # Tenta uma query mais simples
            try:
                cur.execute("""
                    SELECT COUNT(*) as count 
                    FROM aulas a 
                    LEFT JOIN turmas t ON a.turma_id = t.id 
                    WHERE a.is_active = true 
                    AND (t.nome ILIKE '%infantil%' OR t.nome ILIKE '%pré%' OR t.nome ILIKE '%pre%' OR t.nome ILIKE '%básico%')
                """)
                count = cur.fetchone()['count']
                print(f"📊 Total de aulas infantis: {count}")
            except:
                print("⚠️ Query de contagem também falhou")
            # Se não encontrar aulas, retorna lista vazia
            aulas_infantil = []
        
        # Progresso por categorias
        progresso_categorias = {
            'alfabeto': 75,
            'numeros': 60,
            'cores': 45,
            'animais': 30
        }
        
        # Conquistas baseadas no progresso
        total_aulas_concluidas = 5  # Simulado
        conquistas = []
        if total_aulas_concluidas >= 1:
            conquistas.append({'nome': 'Primeira Aula', 'icone': 'star', 'conquistada': True})
        if total_aulas_concluidas >= 5:
            conquistas.append({'nome': '5 Aulas', 'icone': 'check-circle', 'conquistada': True})
        
        cur.close()
        
        return render_template('kids_dashboard.html', 
                             aulas_infantil=aulas_infantil,
                             progresso_categorias=progresso_categorias,
                             conquistas=conquistas)
        
    except Exception as e:
        import traceback
        print(f"❌ ERRO DETALHADO no kids_dashboard: {e}")
        traceback.print_exc()
        flash('❌ Erro ao carregar dashboard infantil!', 'error')
        return render_template('kids_dashboard.html', aulas_infantil=[], progresso_categorias={}, conquistas=[])

# Rota para anos iniciais (1º ao 5º ano)
@app.route('/student/anos-iniciais')
@login_required
@aluno_required
def anos_iniciais():
    """Dashboard para anos iniciais (1º ao 5º ano) - Ensino Fundamental"""
    try:
        print(f"🔍 DEBUG: anos_iniciais chamado para usuário {current_user.id}")
        
        db = get_db()
        cur = db.cursor()
        
        # Buscar aulas específicas para anos iniciais (1º ao 5º ano)
        print("🔍 Executando query para anos_iniciais...")
        try:
            # Query corrigida para usar as colunas que realmente existem
            cur.execute("""
                SELECT a.id, a.titulo, a.descricao, 
                       45 as duracao_minutos, 
                       t.nome as turma_nome, t.descricao as turma_descricao
                FROM aulas a
                LEFT JOIN turmas t ON a.turma_id = t.id
                WHERE a.is_active = true 
                AND (t.nome ILIKE '%1º%' OR t.nome ILIKE '%2º%' OR t.nome ILIKE '%3º%' OR t.nome ILIKE '%4º%' OR t.nome ILIKE '%5º%'
                     OR t.nome ILIKE '%primeiro%' OR t.nome ILIKE '%segundo%' OR t.nome ILIKE '%terceiro%' OR t.nome ILIKE '%quarto%' OR t.nome ILIKE '%quinto%')
                ORDER BY t.nome, a.id DESC
                LIMIT 15
            """)
            print("✅ Query anos_iniciais executada com sucesso!")
            aulas_anos_iniciais = cur.fetchall()
        except Exception as query_error:
            print(f"❌ Erro na query anos_iniciais: {query_error}")
            # Tenta uma query mais simples
            try:
                cur.execute("""
                    SELECT COUNT(*) as count 
                    FROM aulas a 
                    LEFT JOIN turmas t ON a.turma_id = t.id 
                    WHERE a.is_active = true 
                    AND (t.nome ILIKE '%1º%' OR t.nome ILIKE '%2º%' OR t.nome ILIKE '%3º%' OR t.nome ILIKE '%4º%' OR t.nome ILIKE '%5º%'
                         OR t.nome ILIKE '%primeiro%' OR t.nome ILIKE '%segundo%' OR t.nome ILIKE '%terceiro%' OR t.nome ILIKE '%quarto%' OR t.nome ILIKE '%quinto%')
                """)
                count = cur.fetchone()['count']
                print(f"📊 Total de aulas anos iniciais: {count}")
            except:
                print("⚠️ Query de contagem também falhou")
            # Se não encontrar aulas, retorna lista vazia
            aulas_anos_iniciais = []
        
        cur.close()
        
        # Dados específicos para anos iniciais
        progresso_materias = {
            'portugues': 65,
            'matematica': 70,
            'ciencias': 55,
            'historia': 60,
            'geografia': 50
        }
        
        conquistas_anos_iniciais = [
            {'nome': 'Leitor Iniciante', 'descricao': 'Completou 3 aulas de português', 'icone': '📖'},
            {'nome': 'Matemático', 'descricao': 'Completou 5 exercícios de matemática', 'icone': '🔢'},
            {'nome': 'Cientista', 'descricao': 'Completou 2 aulas de ciências', 'icone': '🔬'},
            {'nome': 'Historiador', 'descricao': 'Completou 3 aulas de história', 'icone': '📚'},
            {'nome': 'Geógrafo', 'descricao': 'Completou 2 aulas de geografia', 'icone': '🌍'}
        ]
        
        return render_template('anos_iniciais_dashboard.html', 
                             aulas=aulas_anos_iniciais,
                             progresso_materias=progresso_materias,
                             conquistas=conquistas_anos_iniciais)
                             
    except Exception as e:
        import traceback
        print(f"❌ ERRO DETALHADO no anos_iniciais: {e}")
        traceback.print_exc()
        flash('❌ Erro ao carregar dashboard dos Anos Iniciais!', 'error')
        return redirect(url_for('student_dashboard'))

# Rota para anos finais (6º ao 9º ano)
@app.route('/student/anos-finais')
@login_required
@aluno_required
def anos_finais():
    """Dashboard para anos finais (6º ao 9º ano) - Ensino Fundamental"""
    try:
        print(f"🔍 DEBUG: anos_finais chamado para usuário {current_user.id}")
        
        db = get_db()
        cur = db.cursor()
        
        # Buscar aulas específicas para anos finais (6º ao 9º ano)
        print("🔍 Executando query para anos_finais...")
        try:
            # Query corrigida para usar as colunas que realmente existem
            cur.execute("""
                SELECT a.id, a.titulo, a.descricao, 
                       45 as duracao_minutos, 
                       t.nome as turma_nome, t.descricao as turma_descricao
                FROM aulas a
                LEFT JOIN turmas t ON a.turma_id = t.id
                WHERE a.is_active = true 
                AND (t.nome ILIKE '%6º%' OR t.nome ILIKE '%7º%' OR t.nome ILIKE '%8º%' OR t.nome ILIKE '%9º%'
                     OR t.nome ILIKE '%sexto%' OR t.nome ILIKE '%sétimo%' OR t.nome ILIKE '%oitavo%' OR t.nome ILIKE '%nono%')
                ORDER BY t.nome, a.id DESC
                LIMIT 15
            """)
            print("✅ Query anos_finais executada com sucesso!")
            aulas_anos_finais = cur.fetchall()
        except Exception as query_error:
            print(f"❌ Erro na query anos_finais: {query_error}")
            # Tenta uma query mais simples
            try:
                cur.execute("""
                    SELECT COUNT(*) as count 
                    FROM aulas a 
                    LEFT JOIN turmas t ON a.turma_id = t.id 
                    WHERE a.is_active = true 
                    AND (t.nome ILIKE '%6º%' OR t.nome ILIKE '%7º%' OR t.nome ILIKE '%8º%' OR t.nome ILIKE '%9º%'
                         OR t.nome ILIKE '%sexto%' OR t.nome ILIKE '%sétimo%' OR t.nome ILIKE '%oitavo%' OR t.nome ILIKE '%nono%')
                """)
                count = cur.fetchone()['count']
                print(f"📊 Total de aulas anos finais: {count}")
            except:
                print("⚠️ Query de contagem também falhou")
            # Se não encontrar aulas, retorna lista vazia
            aulas_anos_finais = []
        
        cur.close()
        
        # Dados específicos para anos finais
        progresso_materias = {
            'portugues': 75,
            'matematica': 80,
            'ciencias': 70,
            'historia': 65,
            'geografia': 60,
            'ingles': 55,
            'artes': 45,
            'educacao_fisica': 70
        }
        
        conquistas_anos_finais = [
            {'nome': 'Leitor Avançado', 'descricao': 'Completou 5 aulas de português', 'icone': '📚'},
            {'nome': 'Matemático Avançado', 'descricao': 'Completou 8 exercícios de matemática', 'icone': '🧮'},
            {'nome': 'Cientista Júnior', 'descricao': 'Completou 4 aulas de ciências', 'icone': '⚗️'},
            {'nome': 'Historiador Júnior', 'descricao': 'Completou 4 aulas de história', 'icone': '🏛️'},
            {'nome': 'Geógrafo Júnior', 'descricao': 'Completou 3 aulas de geografia', 'icone': '🗺️'},
            {'nome': 'Falante de Inglês', 'descricao': 'Completou 3 aulas de inglês', 'icone': '🇺🇸'},
            {'nome': 'Artista', 'descricao': 'Completou 2 aulas de artes', 'icone': '🎨'},
            {'nome': 'Atleta', 'descricao': 'Completou 3 aulas de educação física', 'icone': '⚽'}
        ]
        
        return render_template('anos_finais_dashboard.html', 
                             aulas=aulas_anos_finais,
                             progresso_materias=progresso_materias,
                             conquistas=conquistas_anos_finais)
                             
    except Exception as e:
        import traceback
        print(f"❌ ERRO DETALHADO no anos_finais: {e}")
        traceback.print_exc()
        flash('❌ Erro ao carregar dashboard dos Anos Finais!', 'error')
        return redirect(url_for('student_dashboard'))

@app.route('/exercicio/<int:exercicio_id>')
@login_required
def ver_exercicio(exercicio_id):
    """Visualizar um exercício específico"""
    try:
        db = get_db()
        cur = db.cursor()
        
        # Buscar dados do exercício
        cur.execute("""
            SELECT e.*, a.titulo as aula_titulo, a.id as aula_id
            FROM exercicios e
            JOIN aulas a ON e.aula_id = a.id
            WHERE e.id = %s AND e.is_active = true
        """, (exercicio_id,))
        
        exercicio = cur.fetchone()
        if not exercicio:
            flash('❌ Exercício não encontrado!', 'error')
            return redirect(url_for('student_dashboard'))
        
        # Buscar progresso do aluno na aula
        cur.execute("""
            SELECT status, data_inicio, data_conclusao, tempo_gasto
            FROM progresso_alunos
            WHERE aluno_id = %s AND aula_id = %s
        """, (current_user.id, exercicio.aula_id))
        
        progresso_raw = cur.fetchone()
        
        # Calcular percentual de progresso
        if progresso_raw:
            if progresso_raw['status'] == 'concluida':
                percentual = 100
            elif progresso_raw['status'] == 'em_progresso':
                percentual = 50
            else:
                percentual = 25
        else:
            percentual = 0
            
        progresso = {
            'status': progresso_raw['status'] if progresso_raw else 'não iniciada',
            'percentual': percentual,
            'tempo_gasto': progresso_raw['tempo_gasto'] if progresso_raw and progresso_raw['tempo_gasto'] else 0
        }
        
        # Buscar estatísticas do aluno
        cur.execute("""
            SELECT 
                COUNT(CASE WHEN ra.resposta_correta = true THEN 1 END) as acertos,
                COUNT(CASE WHEN ra.resposta_correta = false THEN 1 END) as erros,
                COALESCE(SUM(CASE WHEN ra.resposta_correta = true THEN e.pontos END), 0) as pontos_ganhos,
                COUNT(CASE WHEN ra.resposta_correta = true THEN 1 END) as sequencia
            FROM exercicios e
            LEFT JOIN respostas_alunos ra ON e.id = ra.exercicio_id AND ra.aluno_id = %s
            WHERE e.aula_id = %s
        """, (current_user.id, exercicio.aula_id))
        
        stats_raw = cur.fetchone()
        stats = {
            'acertos': stats_raw['acertos'] or 0,
            'erros': stats_raw['erros'] or 0,
            'pontos_ganhos': stats_raw['pontos_ganhos'] or 0,
            'sequencia': stats_raw['sequencia'] or 0
        }
        
        # Buscar próximos exercícios da mesma aula
        cur.execute("""
            SELECT id, titulo, tipo, pontos
            FROM exercicios
            WHERE aula_id = %s AND id != %s AND is_active = true
            ORDER BY id
            LIMIT 5
        """, (exercicio.aula_id, exercicio_id))
        
        proximos_exercicios = cur.fetchall()
        
        cur.close()
        
        return render_template('exercise.html', 
                             exercicio=exercicio, 
                             progresso=progresso,
                             stats=stats,
                             proximos_exercicios=proximos_exercicios)
                             
    except Exception as e:
        print(f"Erro ao carregar exercício: {e}")
        flash('❌ Erro ao carregar o exercício!', 'error')
        return redirect(url_for('student_dashboard'))

# Rota de teste para verificar se o problema está no redirecionamento automático
@app.route('/test-redirect')
@login_required
@aluno_required
def test_redirect():
    """Rota de teste para verificar redirecionamento"""
    print(f"🔍 DEBUG: ===== TESTE DE REDIRECIONAMENTO =====")
    print(f"🔍 DEBUG: Usuário ID: {current_user.id}")
    print(f"🔍 DEBUG: Usuário Type: {current_user.user_type}")
    print(f"🔍 DEBUG: is_aluno: {current_user.is_aluno}")
    print(f"🔍 DEBUG: ===== FIM TESTE =====")
    
    return f"""
    <h1>Teste de Redirecionamento</h1>
    <p><strong>ID:</strong> {current_user.id}</p>
    <p><strong>Username:</strong> {current_user.username}</p>
    <p><strong>User Type:</strong> {current_user.user_type}</p>
    <p><strong>is_aluno:</strong> {current_user.is_aluno}</p>
    <p><strong>Nome:</strong> {current_user.first_name} {current_user.last_name}</p>
    <br>
    <a href="/student/dashboard">Ir para Dashboard do Aluno</a>
    <br>
    <a href="/student/educacao-basica">Ir para Educação Básica</a>
    <br>
    <a href="/">Voltar ao Início</a>
    """

if __name__ == '__main__':
    # Criar usuários padrão na primeira execução
    with app.app_context():
        create_default_users()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
