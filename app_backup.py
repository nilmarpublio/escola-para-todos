from flask import Flask, render_template, redirect, url_for, flash, request, session, g, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import sqlite3
from dotenv import load_dotenv

# Importar modelos e autenticação
from models import User
from auth import admin_required, professor_required, aluno_required, content_creator_required, user_management_required, analytics_required, guest_required

# Carregar variáveis de ambiente
load_dotenv()

# Inicialização da aplicação
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configurações da aplicação
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas
app.config['SESSION_COOKIE_SECURE'] = False  # True em produção com HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '🔐 Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Carrega usuário para o Flask-Login"""
    db = get_db()
    return User.get_by_id(int(user_id), db)

def get_db():
    """Conectar ao banco de dados SQLite"""
    if 'db' not in g:
        g.db = sqlite3.connect('escola_para_todos.db')
        g.db.row_factory = sqlite3.Row
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

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Editar perfil do usuário"""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        
        if not all([first_name, last_name, email]):
            flash('❌ Por favor, preencha todos os campos.', 'error')
            return render_template('edit_profile.html')
        
        try:
            db = get_db()
            current_user.update_profile(first_name, last_name, email, db)
            flash('✅ Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            flash(f'❌ Erro ao atualizar perfil: {str(e)}', 'error')
    
    return render_template('edit_profile.html')

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Alterar senha do usuário"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            flash('❌ Por favor, preencha todos os campos.', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('❌ As novas senhas não coincidem.', 'error')
            return render_template('change_password.html')
        
        if len(new_password) < 6:
            flash('❌ A nova senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('change_password.html')
        
        # Verificar senha atual
        db = get_db()
        if not check_password_hash(current_user.password_hash, current_password):
            flash('❌ Senha atual incorreta.', 'error')
            return render_template('change_password.html')
        
        try:
            current_user.change_password(new_password, db)
            flash('✅ Senha alterada com sucesso!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            flash(f'❌ Erro ao alterar senha: {str(e)}', 'error')
    
    return render_template('change_password.html')

# =====================================================
# DASHBOARDS
# =====================================================



@app.route('/professor')
@professor_required
def professor_dashboard():
    """Dashboard do professor"""
    db = get_db()
    
    # Buscar aulas criadas pelo professor
    cur = db.cursor()
    cur.execute('''
        SELECT id, titulo, disciplina, serie, created_at 
        FROM aulas 
        WHERE professor_id = ? 
        ORDER BY created_at DESC
    ''', (current_user.id,))
    aulas = cur.fetchall()
    
    # Buscar turmas do professor
    cur.execute('''
        SELECT id, nome, serie, created_at 
        FROM turmas 
        WHERE professor_id = ? 
        ORDER BY created_at DESC
    ''', (current_user.id,))
    turmas = cur.fetchall()
    
    # Estatísticas básicas
    cur.execute('''
        SELECT COUNT(*) as total_alunos
        FROM aluno_turma at
        JOIN turmas t ON at.turma_id = t.id
        WHERE t.professor_id = ? AND (at.status = 'ativo' OR at.status IS NULL)
    ''', (current_user.id,))
    total_alunos = cur.fetchone()['total_alunos']
    
    cur.close()
    
    data = {
        'aulas': aulas,
        'turmas': turmas,
        'total_aulas': len(aulas),
        'total_turmas': len(turmas),
        'total_alunos': total_alunos
    }
    
    return render_template('professor_dashboard.html', data=data)

# =====================================================
# GESTÃO DE AULAS (PROFESSOR)
# =====================================================

@app.route('/professor/aulas')
@professor_required
def professor_aulas():
    """Lista de aulas do professor"""
    db = get_db()
    cur = db.cursor()
    
    cur.execute('''
        SELECT id, titulo, descricao, disciplina, serie, duracao_minutos, created_at
        FROM aulas 
        WHERE professor_id = ? 
        ORDER BY created_at DESC
    ''', (current_user.id,))
    aulas = cur.fetchall()
    
    cur.close()
    
    return render_template('professor_aulas.html', aulas=aulas)

@app.route('/professor/aulas/criar', methods=['GET', 'POST'])
@professor_required
def criar_aula():
    """Criar nova aula"""
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        disciplina = request.form.get('disciplina')
        serie = request.form.get('serie')
        link_video = request.form.get('link_video')
        duracao_minutos = request.form.get('duracao_minutos', 0)
        
        if not all([titulo, descricao, disciplina, serie]):
            flash('❌ Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('professor_criar_aula.html')
        
        try:
            db = get_db()
            cur = db.cursor()
            
            cur.execute('''
                INSERT INTO aulas (titulo, descricao, disciplina, serie, link_video, 
                                 duracao_minutos, professor_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (titulo, descricao, disciplina, serie, link_video, duracao_minutos, current_user.id))
            
            db.commit()
            cur.close()
            
            flash('✅ Aula criada com sucesso!', 'success')
            return redirect(url_for('professor_aulas'))
            
        except Exception as e:
            flash(f'❌ Erro ao criar aula: {str(e)}', 'error')
    
    return render_template('professor_criar_aula.html')

@app.route('/professor/aulas/<int:aula_id>/editar', methods=['GET', 'POST'])
@professor_required
def editar_aula(aula_id):
    """Editar aula existente"""
    db = get_db()
    cur = db.cursor()
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        disciplina = request.form.get('disciplina')
        serie = request.form.get('serie')
        link_video = request.form.get('link_video')
        duracao_minutos = request.form.get('duracao_minutos', 0)
        
        if not all([titulo, descricao, disciplina, serie]):
            flash('❌ Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('professor_editar_aula.html', aula=aula)
        
        try:
        cur.execute('''
                UPDATE aulas 
                SET titulo = ?, descricao = ?, disciplina = ?, serie = ?, 
                    link_video = ?, duracao_minutos = ?
                WHERE id = ? AND professor_id = ?
            ''', (titulo, descricao, disciplina, serie, link_video, duracao_minutos, aula_id, current_user.id))
            
            db.commit()
            flash('✅ Aula atualizada com sucesso!', 'success')
            return redirect(url_for('professor_aulas'))
            
        except Exception as e:
            flash(f'❌ Erro ao atualizar aula: {str(e)}', 'error')
    
    # GET: buscar aula para edição
        cur.execute('''
        SELECT id, titulo, descricao, disciplina, serie, link_video, duracao_minutos
        FROM aulas 
        WHERE id = ? AND professor_id = ?
    ''', (aula_id, current_user.id))
    aula = cur.fetchone()
    
    if not aula:
        flash('❌ Aula não encontrada.', 'error')
        return redirect(url_for('professor_aulas'))
    
    cur.close()
    
    return render_template('professor_editar_aula.html', aula=aula)

@app.route('/professor/aulas/<int:aula_id>/excluir', methods=['POST'])
@professor_required
def excluir_aula(aula_id):
    """Excluir aula"""
    try:
        db = get_db()
        cur = db.cursor()
        
        # Verificar se a aula pertence ao professor
        cur.execute('SELECT id FROM aulas WHERE id = ? AND professor_id = ?', 
                   (aula_id, current_user.id))
        if not cur.fetchone():
            flash('❌ Aula não encontrada.', 'error')
            return redirect(url_for('professor_aulas'))
        
        # Excluir exercícios da aula primeiro
        cur.execute('DELETE FROM exercicios WHERE aula_id = ?', (aula_id,))
        
        # Excluir progresso dos alunos
        cur.execute('DELETE FROM progresso WHERE aula_id = ?', (aula_id,))
        
        # Excluir a aula
        cur.execute('DELETE FROM aulas WHERE id = ?', (aula_id,))
        
        db.commit()
        cur.close()
        
        flash('✅ Aula excluída com sucesso!', 'success')
        
    except Exception as e:
        flash(f'❌ Erro ao excluir aula: {str(e)}', 'error')
    
    return redirect(url_for('professor_aulas'))

# =====================================================
# GESTÃO DE EXERCÍCIOS (PROFESSOR)
# =====================================================

@app.route('/professor/aulas/<int:aula_id>/exercicios')
@professor_required
def professor_exercicios(aula_id):
    """Lista de exercícios de uma aula"""
    db = get_db()
    cur = db.cursor()
    
    # Verificar se a aula pertence ao professor
        cur.execute('''
        SELECT id, titulo, disciplina, serie
        FROM aulas 
        WHERE id = ? AND professor_id = ?
    ''', (aula_id, current_user.id))
    aula = cur.fetchone()
    
    if not aula:
        flash('❌ Aula não encontrada.', 'error')
        return redirect(url_for('professor_aulas'))
    
    # Buscar exercícios da aula
        cur.execute('''
        SELECT id, enunciado, alternativas, resposta_correta
        FROM exercicios 
        WHERE aula_id = ? 
        ORDER BY id
    ''', (aula_id,))
    exercicios = cur.fetchall()
    
    cur.close()
    
    return render_template('professor_exercicios.html', aula=aula, exercicios=exercicios)

@app.route('/professor/aulas/<int:aula_id>/exercicios/criar', methods=['GET', 'POST'])
@professor_required
def criar_exercicio(aula_id):
    """Criar novo exercício para uma aula"""
    db = get_db()
    cur = db.cursor()
    
    # Verificar se a aula pertence ao professor
    cur.execute('SELECT id, titulo FROM aulas WHERE id = ? AND professor_id = ?', 
               (aula_id, current_user.id))
    aula = cur.fetchone()
    
    if not aula:
        flash('❌ Aula não encontrada.', 'error')
        return redirect(url_for('professor_aulas'))
    
    if request.method == 'POST':
        enunciado = request.form.get('enunciado')
        alternativas = request.form.get('alternativas')
        resposta_correta = request.form.get('resposta_correta')
        
        if not all([enunciado, alternativas, resposta_correta]):
            flash('❌ Por favor, preencha todos os campos.', 'error')
            return render_template('professor_criar_exercicio.html', aula=aula)
        
        try:
        cur.execute('''
                INSERT INTO exercicios (enunciado, alternativas, resposta_correta, aula_id)
                VALUES (?, ?, ?, ?)
            ''', (enunciado, alternativas, resposta_correta, aula_id))
            
            db.commit()
            flash('✅ Exercício criado com sucesso!', 'success')
            return redirect(url_for('professor_exercicios', aula_id=aula_id))
            
        except Exception as e:
            flash(f'❌ Erro ao criar exercício: {str(e)}', 'error')
    
    cur.close()
    
    return render_template('professor_criar_exercicio.html', aula=aula)

@app.route('/professor/exercicios/<int:exercicio_id>/editar', methods=['GET', 'POST'])
@professor_required
def editar_exercicio(exercicio_id):
    """Editar exercício existente"""
    db = get_db()
    cur = db.cursor()
    
    if request.method == 'POST':
        enunciado = request.form.get('enunciado')
        alternativas = request.form.get('alternativas')
        resposta_correta = request.form.get('resposta_correta')
        
        if not all([enunciado, alternativas, resposta_correta]):
            flash('❌ Por favor, preencha todos os campos.', 'error')
            return render_template('professor_editar_exercicio.html', exercicio=exercicio)
        
        try:
        cur.execute('''
                UPDATE exercicios 
                SET enunciado = ?, alternativas = ?, resposta_correta = ?
                WHERE id = ? AND aula_id IN (
                    SELECT id FROM aulas WHERE professor_id = ?
                )
            ''', (enunciado, alternativas, resposta_correta, exercicio_id, current_user.id))
            
            db.commit()
            flash('✅ Exercício atualizado com sucesso!', 'success')
            return redirect(url_for('professor_exercicios', aula_id=exercicio['aula_id']))
            
        except Exception as e:
            flash(f'❌ Erro ao atualizar exercício: {str(e)}', 'error')
    
    # GET: buscar exercício para edição
        cur.execute('''
        SELECT e.id, e.enunciado, e.alternativas, e.resposta_correta, e.aula_id,
               a.titulo as aula_titulo
        FROM exercicios e
        JOIN aulas a ON e.aula_id = a.id
        WHERE e.id = ? AND a.professor_id = ?
    ''', (exercicio_id, current_user.id))
    exercicio = cur.fetchone()
    
    if not exercicio:
        flash('❌ Exercício não encontrado.', 'error')
        return redirect(url_for('professor_aulas'))
    
    cur.close()
    
    return render_template('professor_editar_exercicio.html', exercicio=exercicio)

@app.route('/professor/exercicios/<int:exercicio_id>/excluir', methods=['POST'])
@professor_required
def excluir_exercicio(exercicio_id):
    """Excluir exercício"""
    try:
        db = get_db()
        cur = db.cursor()
        
        # Buscar aula_id antes de excluir
        cur.execute('''
            SELECT e.aula_id 
            FROM exercicios e
            JOIN aulas a ON e.aula_id = a.id
            WHERE e.id = ? AND a.professor_id = ?
        ''', (exercicio_id, current_user.id))
        
        result = cur.fetchone()
        if not result:
            flash('❌ Exercício não encontrado.', 'error')
            return redirect(url_for('professor_aulas'))
        
        aula_id = result[0]
        
        # Excluir o exercício
        cur.execute('DELETE FROM exercicios WHERE id = ?', (exercicio_id,))
        db.commit()
        
        flash('✅ Exercício excluído com sucesso!', 'success')
        return redirect(url_for('professor_exercicios', aula_id=aula_id))
        
    except Exception as e:
        flash(f'❌ Erro ao excluir exercício: {str(e)}', 'error')
        return redirect(url_for('professor_aulas'))
    
    finally:
        cur.close()

# =====================================================
# GESTÃO DE TURMAS (PROFESSOR)
# =====================================================

@app.route('/professor/turmas')
@professor_required
def professor_turmas():
    """Lista de turmas do professor"""
    db = get_db()
    cur = db.cursor()
    
    cur.execute('''
        SELECT id, nome, serie, created_at
        FROM turmas 
        WHERE professor_id = ? 
        ORDER BY serie, nome
    ''', (current_user.id,))
    turmas = cur.fetchall()
    
    cur.close()
    
    return render_template('professor_turmas.html', turmas=turmas)

@app.route('/professor/turmas/criar', methods=['GET', 'POST'])
@professor_required
def criar_turma():
    """Criar nova turma"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        serie = request.form.get('serie')
        
        if not all([nome, serie]):
            flash('❌ Por favor, preencha todos os campos.', 'error')
            return render_template('professor_criar_turma.html')
        
        try:
        db = get_db()
            cur = db.cursor()
            
            cur.execute('''
                INSERT INTO turmas (nome, serie, professor_id, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (nome, serie, current_user.id))
            
            db.commit()
        cur.close()
        
            flash('✅ Turma criada com sucesso!', 'success')
            return redirect(url_for('professor_turmas'))
            
        except Exception as e:
            flash(f'❌ Erro ao criar turma: {str(e)}', 'error')
    
    return render_template('professor_criar_turma.html')

@app.route('/professor/turmas/<int:turma_id>')
@professor_required
def professor_turma_detalhes(turma_id):
    """Detalhes de uma turma específica"""
    db = get_db()
    cur = db.cursor()
    
    # Verificar se a turma pertence ao professor
    cur.execute('''
        SELECT id, nome, serie, created_at
        FROM turmas 
        WHERE id = ? AND professor_id = ?
    ''', (turma_id, current_user.id))
    turma = cur.fetchone()
    
    if not turma:
        flash('❌ Turma não encontrada.', 'error')
        return redirect(url_for('professor_turmas'))
    
    # Buscar alunos da turma
    cur.execute('''
        SELECT u.id, u.username, u.first_name, u.last_name, u.email, at.data_matricula, at.status
        FROM aluno_turma at
        JOIN users u ON at.aluno_id = u.id
        WHERE at.turma_id = ? AND (at.status = 'ativo' OR at.status IS NULL)
        ORDER BY u.first_name, u.last_name
    ''', (turma_id,))
    alunos = cur.fetchall()
    
    # Buscar aulas da turma
    cur.execute('''
        SELECT id, titulo, disciplina, duracao_minutos
        FROM aulas 
        WHERE serie = ? AND professor_id = ?
        ORDER BY disciplina, titulo
    ''', (turma['serie'], current_user.id))
    aulas = cur.fetchall()
    
    cur.close()
    
    return render_template('professor_turma_detalhes.html', 
                         turma=turma, alunos=alunos, aulas=aulas)

@app.route('/professor/turmas/<int:turma_id>/adicionar-aluno', methods=['POST'])
@professor_required
def adicionar_aluno_turma(turma_id):
    """Adicionar aluno à turma"""
    username = request.form.get('username')
    
    if not username:
        flash('❌ Por favor, informe o username do aluno.', 'error')
        return redirect(url_for('professor_turma_detalhes', turma_id=turma_id))
    
    try:
        db = get_db()
        cur = db.cursor()
        
        # Verificar se a turma pertence ao professor
        cur.execute('SELECT id FROM turmas WHERE id = ? AND professor_id = ?', 
                   (turma_id, current_user.id))
        if not cur.fetchone():
            flash('❌ Turma não encontrada.', 'error')
            return redirect(url_for('professor_turmas'))
        
        # Buscar aluno pelo username
        cur.execute('SELECT id FROM users WHERE username = ? AND user_type = "aluno"', (username,))
        aluno = cur.fetchone()
        
        if not aluno:
            flash('❌ Aluno não encontrado.', 'error')
            return redirect(url_for('professor_turma_detalhes', turma_id=turma_id))
        
        # Verificar se já está matriculado
        cur.execute('SELECT id FROM aluno_turma WHERE aluno_id = ? AND turma_id = ?', 
                   (aluno['id'], turma_id))
        if cur.fetchone():
            flash('❌ Aluno já está matriculado nesta turma.', 'error')
            return redirect(url_for('professor_turma_detalhes', turma_id=turma_id))
        
        # Matricular aluno
        cur.execute('''
            INSERT INTO aluno_turma (aluno_id, turma_id, data_matricula, status)
            VALUES (?, ?, CURRENT_TIMESTAMP, 'ativo')
        ''', (aluno['id'], turma_id))
        
        db.commit()
            cur.close()
        
        flash('✅ Aluno adicionado à turma com sucesso!', 'success')
        
    except Exception as e:
        flash(f'❌ Erro ao adicionar aluno: {str(e)}', 'error')
    
    return redirect(url_for('professor_turma_detalhes', turma_id=turma_id))

@app.route('/professor/turmas/<int:turma_id>/remover-aluno/<int:aluno_id>', methods=['POST'])
@professor_required
def remover_aluno_turma(turma_id, aluno_id):
    """Remover aluno da turma"""
    try:
        db = get_db()
        cur = db.cursor()
        
        # Verificar se a turma pertence ao professor
        cur.execute('SELECT id FROM turmas WHERE id = ? AND professor_id = ?', 
                   (turma_id, current_user.id))
        if not cur.fetchone():
            flash('❌ Turma não encontrada.', 'error')
            return redirect(url_for('professor_turmas'))
        
        # Remover matrícula
        cur.execute('DELETE FROM aluno_turma WHERE aluno_id = ? AND turma_id = ?', 
                   (aluno_id, turma_id))
        
        db.commit()
        cur.close()
        
        flash('✅ Aluno removido da turma com sucesso!', 'success')
        
    except Exception as e:
        flash(f'❌ Erro ao remover aluno: {str(e)}', 'error')
    
    return redirect(url_for('professor_turma_detalhes', turma_id=turma_id))

# =====================================================
# RELATÓRIOS DE DESEMPENHO (PROFESSOR)
# =====================================================

@app.route('/professor/relatorios')
@professor_required
def professor_relatorios():
    """Página principal de relatórios"""
    return render_template('professor_relatorios.html')

@app.route('/professor/relatorios/turma/<int:turma_id>')
@professor_required
def relatorio_turma(turma_id):
    """Relatório de desempenho de uma turma específica"""
    db = get_db()
    cur = db.cursor()
    
    # Verificar se a turma pertence ao professor
        cur.execute('''
        SELECT id, nome, serie
        FROM turmas 
        WHERE id = ? AND professor_id = ?
    ''', (turma_id, current_user.id))
    turma = cur.fetchone()
    
    if not turma:
        flash('❌ Turma não encontrada.', 'error')
        return redirect(url_for('professor_relatorios'))
    
    # Buscar alunos da turma com progresso
            cur.execute('''
        SELECT u.id, u.first_name, u.last_name, u.username,
               COUNT(DISTINCT a.id) as total_aulas,
               COUNT(DISTINCT CASE WHEN p.status = 'concluido' THEN a.id END) as aulas_concluidas,
               SUM(COALESCE(p.pontuacao, 0)) as total_pontos,
               AVG(COALESCE(p.pontuacao, 0)) as media_pontos
        FROM users u
        JOIN aluno_turma at ON u.id = at.aluno_id
        LEFT JOIN aulas a ON a.serie = ? AND a.professor_id = ?
        LEFT JOIN progresso p ON a.id = p.aula_id AND p.aluno_id = u.id
        WHERE at.turma_id = ? AND (at.status = 'ativo' OR at.status IS NULL)
        GROUP BY u.id, u.first_name, u.last_name, u.username
        ORDER BY u.first_name, u.last_name
    ''', (turma['serie'], current_user.id, turma_id))
    alunos_progresso = cur.fetchall()
    
    # Estatísticas da turma
    total_alunos = len(alunos_progresso)
    if total_alunos > 0:
        media_turma = sum(aluno['media_pontos'] for aluno in alunos_progresso) / total_alunos
        total_aulas_turma = alunos_progresso[0]['total_aulas'] if alunos_progresso else 0
    else:
        media_turma = 0
        total_aulas_turma = 0
    
        cur.close()
        
    return render_template('professor_relatorio_turma.html', 
                         turma=turma, 
                         alunos_progresso=alunos_progresso,
                         total_alunos=total_alunos,
                         media_turma=media_turma,
                         total_aulas_turma=total_aulas_turma)

@app.route('/professor/relatorios/aluno/<int:aluno_id>')
@professor_required
def relatorio_aluno(aluno_id):
    """Relatório de desempenho de um aluno específico"""
    db = get_db()
    cur = db.cursor()
    
    # Verificar se o aluno está em uma turma do professor
    cur.execute('''
        SELECT u.id, u.first_name, u.last_name, u.username, u.email,
               t.id as turma_id, t.nome as turma_nome, t.serie as turma_serie
        FROM users u
        JOIN aluno_turma at ON u.id = at.aluno_id
        JOIN turmas t ON at.turma_id = t.id
        WHERE u.id = ? AND t.professor_id = ? AND (at.status = 'ativo' OR at.status IS NULL)
    ''', (aluno_id, current_user.id))
    aluno_info = cur.fetchone()
    
    if not aluno_info:
        flash('❌ Aluno não encontrado ou não está em suas turmas.', 'error')
        return redirect(url_for('professor_relatorios'))
    
    # Buscar progresso detalhado do aluno
    cur.execute('''
        SELECT a.id, a.titulo, a.disciplina, a.serie,
               p.status, p.pontuacao, p.tempo_assistido, p.ultima_atividade
        FROM aulas a
        LEFT JOIN progresso p ON a.id = p.aula_id AND p.aluno_id = ?
        WHERE a.serie = ? AND a.professor_id = ?
        ORDER BY a.disciplina, a.titulo
    ''', (aluno_id, aluno_info['turma_serie'], current_user.id))
    progresso_aulas = cur.fetchall()
    
    # Estatísticas do aluno
    total_aulas = len(progresso_aulas)
    aulas_concluidas = len([a for a in progresso_aulas if a['status'] == 'concluido'])
    total_pontos = sum([a['pontuacao'] or 0 for a in progresso_aulas])
    tempo_total = sum([a['tempo_assistido'] or 0 for a in progresso_aulas])
    
    if total_aulas > 0:
        percentual_conclusao = (aulas_concluidas / total_aulas) * 100
        media_pontos = total_pontos / total_aulas
    else:
        percentual_conclusao = 0
        media_pontos = 0
    
    cur.close()
    
    return render_template('professor_relatorio_aluno.html',
                         aluno=aluno_info,
                         progresso_aulas=progresso_aulas,
                         total_aulas=total_aulas,
                         aulas_concluidas=aulas_concluidas,
                         total_pontos=total_pontos,
                         tempo_total=tempo_total,
                         percentual_conclusao=percentual_conclusao,
                         media_pontos=media_pontos)

@app.route('/student')
@aluno_required
def student_dashboard():
    """Dashboard do aluno"""
    db = get_db()
    
    # Buscar progresso do aluno
    cur = db.cursor()
    cur.execute('''
        SELECT a.id, a.titulo, a.disciplina, a.serie, p.status, p.pontuacao, p.tempo_assistido, p.ultima_atividade
        FROM aulas a
        LEFT JOIN progresso p ON a.id = p.aula_id AND p.aluno_id = ?
        ORDER BY a.disciplina, a.serie, a.titulo
    ''', (current_user.id,))
    aulas_progresso = cur.fetchall()
    
    # Buscar turmas do aluno
    cur.execute('''
        SELECT t.id, t.nome, t.serie, u.first_name, u.last_name
        FROM aluno_turma at
        JOIN turmas t ON at.turma_id = t.id
        JOIN users u ON t.professor_id = u.id
        WHERE at.aluno_id = ? AND (at.status = 'ativo' OR at.status IS NULL)
    ''', (current_user.id,))
    turmas = cur.fetchall()
    
    # Buscar conquistas do aluno
    cur.execute('''
        SELECT c.nome, c.descricao, c.pontos, ac.data_conquista
        FROM aluno_conquista ac
        JOIN conquistas c ON ac.conquista_id = c.id
        WHERE ac.aluno_id = ?
        ORDER BY ac.data_conquista DESC
    ''', (current_user.id,))
    conquistas = cur.fetchall()
    
    # Calcular estatísticas
    total_aulas = len(aulas_progresso)
    aulas_iniciadas = len([a for a in aulas_progresso if a[4] and a[4] != 'nao_iniciado'])
    aulas_concluidas = len([a for a in aulas_progresso if a[4] == 'concluido'])
    total_pontos = sum([a[5] or 0 for a in aulas_progresso])
    
    cur.close()
    
    data = {
        'aulas_progresso': aulas_progresso,
        'turmas': turmas,
        'conquistas': conquistas,
        'total_aulas': total_aulas,
        'aulas_iniciadas': aulas_iniciadas,
        'aulas_concluidas': aulas_concluidas,
        'total_pontos': total_pontos
    }
    
    return render_template('student_dashboard.html', data=data)

@app.route('/student/aulas')
@aluno_required
def student_aulas():
    """Lista de disciplinas e aulas disponíveis"""
    db = get_db()
    
    # Buscar todas as disciplinas
    cur = db.cursor()
    cur.execute('''
        SELECT DISTINCT disciplina, serie
        FROM aulas
        ORDER BY serie, disciplina
    ''')
    disciplinas = cur.fetchall()
    
    # Buscar aulas por disciplina
    aulas_por_disciplina = {}
    for disc, serie in disciplinas:
        cur.execute('''
            SELECT a.id, a.titulo, a.descricao, a.serie, a.link_video,
                   p.status, p.pontuacao, p.tempo_assistido
            FROM aulas a
            LEFT JOIN progresso p ON a.id = p.aula_id AND p.aluno_id = ?
            WHERE a.disciplina = ? AND a.serie = ?
            ORDER BY a.titulo
        ''', (current_user.id, disc, serie))
        aulas = cur.fetchall()
        aulas_por_disciplina[(disc, serie)] = aulas
    
    cur.close()
    
    return render_template('student_aulas.html', 
                         disciplinas=disciplinas, 
                         aulas_por_disciplina=aulas_por_disciplina)

@app.route('/student/aula/<int:aula_id>')
@aluno_required
def student_aula_view(aula_id):
    """Visualizar aula específica"""
    db = get_db()
    
    cur = db.cursor()
    cur.execute('''
        SELECT a.id, a.titulo, a.descricao, a.disciplina, a.serie, a.link_video,
               p.status, p.pontuacao, p.tempo_assistido
        FROM aulas a
        LEFT JOIN progresso p ON a.id = p.aula_id AND p.aluno_id = ?
        WHERE a.id = ?
    ''', (current_user.id, aula_id))
    aula = cur.fetchone()
    
    if not aula:
        flash('❌ Aula não encontrada.', 'error')
        return redirect(url_for('student_aulas'))
    
    # Buscar exercícios da aula
    cur.execute('''
        SELECT id, enunciado, alternativas, resposta_correta
        FROM exercicios
        WHERE aula_id = ?
        ORDER BY id
    ''', (aula_id,))
    exercicios = cur.fetchall()
    
    cur.close()
    
    return render_template('student_aula_view.html', 
                         aula=aula, 
                         exercicios=exercicios)

@app.route('/student/aula/<int:aula_id>/iniciar', methods=['POST'])
@aluno_required
def iniciar_aula(aula_id):
    """Iniciar uma aula (marcar como em andamento)"""
    db = get_db()
    
    try:
        cur = db.cursor()
        cur.execute('''
            INSERT OR REPLACE INTO progresso (aluno_id, aula_id, status, ultima_atividade)
            VALUES (?, ?, 'em_andamento', CURRENT_TIMESTAMP)
        ''', (current_user.id, aula_id))
        db.commit()
        cur.close()
        
        flash('✅ Aula iniciada com sucesso!', 'success')
    except Exception as e:
        flash(f'❌ Erro ao iniciar aula: {str(e)}', 'error')
    
    return redirect(url_for('student_aula_view', aula_id=aula_id))







@app.route('/student/progresso')
@aluno_required
def student_progresso():
    """Página de progresso detalhado do aluno"""
    db = get_db()
    
    cur = db.cursor()
    
    # Buscar progresso detalhado do aluno
    cur.execute('''
        SELECT a.id, a.titulo, a.disciplina, a.serie, a.duracao_minutos,
               p.status, p.pontuacao, p.tempo_assistido, p.ultima_atividade
        FROM aulas a
        LEFT JOIN progresso p ON a.id = p.aula_id AND p.aluno_id = ?
        ORDER BY a.disciplina, a.serie, a.titulo
    ''', (current_user.id,))
    aulas_progresso = cur.fetchall()
    
    # Calcular estatísticas detalhadas
    total_aulas = len(aulas_progresso)
    aulas_iniciadas = len([a for a in aulas_progresso if a[5] and a[5] != 'nao_iniciado'])
    aulas_concluidas = len([a for a in aulas_progresso if a[5] == 'concluido'])
    total_pontos = sum([a[6] or 0 for a in aulas_progresso])
    tempo_total = sum([a[7] or 0 for a in aulas_progresso])
    
    # Progresso por disciplina
    progresso_disciplina = {}
    for aula in aulas_progresso:
        disc = aula[2]
        if disc not in progresso_disciplina:
            progresso_disciplina[disc] = {'total': 0, 'concluidas': 0, 'pontos': 0}
        
        progresso_disciplina[disc]['total'] += 1
        if aula[5] == 'concluido':
            progresso_disciplina[disc]['concluidas'] += 1
        progresso_disciplina[disc]['pontos'] += aula[6] or 0
    
    # Progresso por série
    progresso_serie = {}
    for aula in aulas_progresso:
        serie = aula[3]
        if serie not in progresso_serie:
            progresso_serie[serie] = {'total': 0, 'concluidas': 0, 'pontos': 0}
        
        progresso_serie[serie]['total'] += 1
        if aula[5] == 'concluido':
            progresso_serie[serie]['concluidas'] += 1
        progresso_serie[serie]['pontos'] += aula[6] or 0
    
    cur.close()
    
    data = {
        'aulas_progresso': aulas_progresso,
        'total_aulas': total_aulas,
        'aulas_iniciadas': aulas_iniciadas,
        'aulas_concluidas': aulas_concluidas,
        'total_pontos': total_pontos,
        'tempo_total': tempo_total,
        'progresso_disciplina': progresso_disciplina,
        'progresso_serie': progresso_serie
    }
    
    return render_template('student_progresso.html', data=data)

@app.route('/student/turmas')
@aluno_required
def student_turmas():
    """Página de turmas do aluno"""
    try:
    db = get_db()
        cur = db.cursor()
        
        # Buscar turmas do aluno com informações detalhadas
        cur.execute('''
            SELECT t.id, t.nome, t.serie, u.first_name, u.last_name, u.email,
                   at.data_matricula, at.status
            FROM aluno_turma at
            JOIN turmas t ON at.turma_id = t.id
            JOIN users u ON t.professor_id = u.id
            WHERE at.aluno_id = ? AND (at.status = 'ativo' OR at.status IS NULL)
            ORDER BY t.serie, t.nome
        ''', (current_user.id,))
        turmas = cur.fetchall()
        
        # Buscar aulas de cada turma
        turmas_com_aulas = []
        for turma in turmas:
            # Primeiro buscar o ID do professor da turma
            cur.execute('''
                SELECT professor_id FROM turmas WHERE id = ?
            ''', (turma[0],))
            professor_id = cur.fetchone()[0]
            
            cur.execute('''
                SELECT a.id, a.titulo, a.disciplina, a.serie, a.duracao_minutos,
                       p.status, p.pontuacao
                FROM aulas a
                LEFT JOIN progresso p ON a.id = p.aula_id AND p.aluno_id = ?
                WHERE a.serie = ? AND a.professor_id = ?
                ORDER BY a.titulo
            ''', (current_user.id, turma[2], professor_id))
            aulas = cur.fetchall()
            
            turmas_com_aulas.append({
                'turma': turma,
                'aulas': aulas
            })
        
        cur.close()
        
        return render_template('student_turmas.html', 
                             turmas_com_aulas=turmas_com_aulas)
    except Exception as e:
        print(f"ERRO na rota student_turmas: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'❌ Erro ao carregar turmas: {str(e)}', 'error')
        return redirect(url_for('student_dashboard'))
    
@app.route('/test-turmas')
@aluno_required
def test_turmas():
    """Rota de teste para verificar dados das turmas"""
    try:
        db = get_db()
        cur = db.cursor()
        
        # Teste 1: Verificar usuário atual
        user_info = f"Usuário: {current_user.username} (ID: {current_user.id}, Tipo: {current_user.user_type})"
        
        # Teste 2: Verificar matrículas
        cur.execute('SELECT * FROM aluno_turma WHERE aluno_id = ?', (current_user.id,))
        matriculas = cur.fetchall()
        matriculas_info = f"Matrículas: {matriculas}"
        
        # Teste 3: Verificar turmas
        cur.execute('''
            SELECT t.id, t.nome, t.serie, u.first_name, u.last_name
            FROM aluno_turma at
            JOIN turmas t ON at.turma_id = t.id
            JOIN users u ON t.professor_id = u.id
            WHERE at.aluno_id = ?
        ''', (current_user.id,))
        turmas = cur.fetchall()
        turmas_info = f"Turmas: {turmas}"
    
    cur.close()
    
        return f"""
        <h1>Teste de Turmas</h1>
        <p><strong>{user_info}</strong></p>
        <p><strong>{matriculas_info}</strong></p>
        <p><strong>{turmas_info}</strong></p>
        <p><a href="/student/turmas">Ir para Minhas Turmas</a></p>
        """
        
    except Exception as e:
        return f"ERRO: {str(e)}"



# =====================================================
# GERENCIAMENTO DE USUÁRIOS (APENAS ADMIN)
# =====================================================

@app.route('/admin/users')
@user_management_required
def manage_users():
    """Gerenciar usuários (apenas admin)"""
    db = get_db()
    users = User.get_all_users(db)
    return render_template('manage_users.html', users=users)

@app.route('/admin/users/<int:user_id>/toggle-status')
@user_management_required
def toggle_user_status(user_id):
    """Ativar/desativar usuário"""
    db = get_db()
    user = User.get_by_id(user_id, db)
    
    if not user:
        flash('❌ Usuário não encontrado.', 'error')
        return redirect(url_for('manage_users'))
    
    if user.id == current_user.id:
        flash('❌ Você não pode desativar sua própria conta.', 'error')
        return redirect(url_for('manage_users'))
    
    try:
        if user.is_active:
            user.deactivate(db)
            flash(f'✅ Usuário {user.username} foi desativado.', 'success')
        else:
            user.activate(db)
            flash(f'✅ Usuário {user.username} foi ativado.', 'success')
    except Exception as e:
        flash(f'❌ Erro ao alterar status do usuário: {str(e)}', 'error')
    
    return redirect(url_for('manage_users'))

@app.route('/admin/users/create', methods=['GET', 'POST'])
@user_management_required
def create_user():
    """Criar novo usuário (apenas admin)"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        user_type = request.form.get('user_type')
        
        if not all([username, email, password, first_name, last_name, user_type]):
            flash('❌ Por favor, preencha todos os campos.', 'error')
            return render_template('create_user.html')
        
        if user_type not in ['aluno', 'professor', 'admin']:
            flash('❌ Tipo de usuário inválido.', 'error')
            return render_template('create_user.html')
        
        try:
            db = get_db()
            
            # Verificar se username já existe
            if User.get_by_username(username, db):
                flash('❌ Este username já está em uso.', 'error')
                return render_template('create_user.html')
            
            # Verificar se email já existe
            if User.get_by_email(email, db):
                flash('❌ Este email já está em uso.', 'error')
                return render_template('create_user.html')
            
            # Criar usuário
            user = User.create_user(username, email, password, first_name, last_name, user_type, db)
            
            flash(f'✅ Usuário {user.username} criado com sucesso!', 'success')
            return redirect(url_for('manage_users'))
            
        except Exception as e:
            flash(f'❌ Erro ao criar usuário: {str(e)}', 'error')
    
    return render_template('create_user.html')

# =====================================================
# PAINEL DO ADMIN
# =====================================================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Dashboard principal do admin com estatísticas globais"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Estatísticas gerais
        cursor.execute("""
            SELECT 
                COUNT(*) as total_usuarios,
                SUM(CASE WHEN user_type = 'aluno' THEN 1 ELSE 0 END) as total_alunos,
                SUM(CASE WHEN user_type = 'professor' THEN 1 ELSE 0 END) as total_professores,
                SUM(CASE WHEN user_type = 'admin' THEN 1 ELSE 0 END) as total_admins
            FROM users
        """)
        stats = cursor.fetchone()
        
        # Total de turmas
        cursor.execute("SELECT COUNT(*) FROM turmas")
        total_turmas = cursor.fetchone()[0]
        
        # Total de aulas
        cursor.execute("SELECT COUNT(*) FROM aulas")
        total_aulas = cursor.fetchone()[0]
        
        # Total de exercícios
        cursor.execute("SELECT COUNT(*) FROM exercicios")
        total_exercicios = cursor.fetchone()[0]
        
        # Progresso médio dos alunos
        cursor.execute("""
            SELECT AVG(pontuacao) as media_progresso
            FROM progresso 
            WHERE pontuacao IS NOT NULL
        """)
        media_progresso = cursor.fetchone()[0] or 0
        
        # Usuários recentes
        cursor.execute("""
            SELECT id, username, email, user_type, created_at
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        usuarios_recentes = cursor.fetchall()
        
        # Turmas recentes
        cursor.execute("""
            SELECT t.id, t.nome, t.serie, u.username as professor, t.created_at
            FROM turmas t
            JOIN users u ON t.professor_id = u.id
            ORDER BY t.created_at DESC 
            LIMIT 5
        """)
        turmas_recentes = cursor.fetchall()
        
        return render_template('admin_dashboard.html', 
                             stats=stats,
                             total_turmas=total_turmas,
                             total_aulas=total_aulas,
                             total_exercicios=total_exercicios,
                             media_progresso=round(media_progresso, 1),
                             usuarios_recentes=usuarios_recentes,
                             turmas_recentes=turmas_recentes)
                             
    except Exception as e:
        flash(f'❌ Erro ao carregar dashboard: {str(e)}', 'error')
    return redirect(url_for('splash'))

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    """Lista todos os usuários do sistema"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Buscar usuários com informações adicionais
        cursor.execute("""
            SELECT 
                u.id, u.username, u.email, u.user_type, u.created_at,
                u.first_name, u.last_name,
                CASE 
                    WHEN u.user_type = 'aluno' THEN (
                        SELECT COUNT(*) FROM aluno_turma at 
                        WHERE at.aluno_id = u.id AND (at.status = 'ativo' OR at.status IS NULL)
                    )
                    WHEN u.user_type = 'professor' THEN (
                        SELECT COUNT(*) FROM turmas t 
                        WHERE t.professor_id = u.id
                    )
                    ELSE 0
                END as contador
            FROM users u
            ORDER BY u.created_at DESC
        """)
        usuarios = cursor.fetchall()
        
        return render_template('admin_usuarios.html', usuarios=usuarios)
        
    except Exception as e:
        flash(f'❌ Erro ao carregar usuários: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/usuarios/criar')
@admin_required
def admin_criar_usuario():
    """Formulário para criar novo usuário"""
    return render_template('admin_criar_usuario.html')

@app.route('/admin/usuarios/criar', methods=['POST'])
@admin_required
def admin_criar_usuario_post():
    """Processa criação de novo usuário"""
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        user_type = request.form.get('user_type')
        
        if not all([username, email, password, first_name, last_name, user_type]):
            flash('❌ Por favor, preencha todos os campos.', 'error')
            return redirect(url_for('admin_criar_usuario'))
        
        if user_type not in ['aluno', 'professor', 'admin']:
            flash('❌ Tipo de usuário inválido.', 'error')
            return redirect(url_for('admin_criar_usuario'))
        
        db = get_db()
        
        # Verificar se username já existe
        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            flash('❌ Este username já está em uso.', 'error')
            return redirect(url_for('admin_criar_usuario'))
        
        # Verificar se email já existe
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            flash('❌ Este email já está em uso.', 'error')
            return redirect(url_for('admin_criar_usuario'))
        
        # Criar usuário
        hashed_password = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, first_name, last_name, user_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (username, email, hashed_password, first_name, last_name, user_type))
        db.commit()
        
        flash(f'✅ Usuário {username} criado com sucesso!', 'success')
        return redirect(url_for('admin_usuarios'))
        
    except Exception as e:
        flash(f'❌ Erro ao criar usuário: {str(e)}', 'error')
        return redirect(url_for('admin_criar_usuario'))

@app.route('/admin/usuarios/<int:user_id>/editar')
@admin_required
def admin_editar_usuario(user_id):
    """Formulário para editar usuário existente"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT id, username, email, first_name, last_name, user_type, created_at
            FROM users WHERE id = ?
        """, (user_id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            flash('❌ Usuário não encontrado.', 'error')
            return redirect(url_for('admin_usuarios'))
        
        return render_template('admin_editar_usuario.html', usuario=usuario)
        
    except Exception as e:
        flash(f'❌ Erro ao carregar usuário: {str(e)}', 'error')
        return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuarios/<int:user_id>/editar', methods=['POST'])
@admin_required
def admin_editar_usuario_post(user_id):
    """Processa edição de usuário"""
    try:
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        user_type = request.form.get('user_type')
        password = request.form.get('password')
        
        if not all([email, first_name, last_name, user_type]):
            flash('❌ Por favor, preencha todos os campos obrigatórios.', 'error')
            return redirect(url_for('admin_editar_usuario', user_id=user_id))
        
        if user_type not in ['aluno', 'professor', 'admin']:
            flash('❌ Tipo de usuário inválido.', 'error')
            return redirect(url_for('admin_editar_usuario', user_id=user_id))
        
        db = get_db()
        cursor = db.cursor()
        
        # Verificar se email já existe em outro usuário
        cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id))
        if cursor.fetchone():
            flash('❌ Este email já está em uso por outro usuário.', 'error')
            return redirect(url_for('admin_editar_usuario', user_id=user_id))
        
        # Atualizar usuário
        if password:
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                UPDATE users 
                SET email = ?, first_name = ?, last_name = ?, user_type = ?, password_hash = ?
                WHERE id = ?
            """, (email, first_name, last_name, user_type, hashed_password, user_id))
        else:
            cursor.execute("""
                UPDATE users 
                SET email = ?, first_name = ?, last_name = ?, user_type = ?
                WHERE id = ?
            """, (email, first_name, last_name, user_type, user_id))
        
        db.commit()
        flash('✅ Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin_usuarios'))
        
    except Exception as e:
        flash(f'❌ Erro ao atualizar usuário: {str(e)}', 'error')
        return redirect(url_for('admin_editar_usuario', user_id=user_id))

@app.route('/admin/usuarios/<int:user_id>/excluir', methods=['POST'])
@admin_required
def admin_excluir_usuario(user_id):
    """Exclui usuário do sistema"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Verificar se é o próprio usuário logado
        if user_id == current_user.id:
            flash('❌ Você não pode excluir sua própria conta.', 'error')
            return redirect(url_for('admin_usuarios'))
        
        # Verificar se usuário existe
        cursor.execute("SELECT username, user_type FROM users WHERE id = ?", (user_id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            flash('❌ Usuário não encontrado.', 'error')
            return redirect(url_for('admin_usuarios'))
        
        # Excluir usuário (cascade será tratado pelo banco)
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        
        flash(f'✅ Usuário {usuario[0]} excluído com sucesso!', 'success')
        return redirect(url_for('admin_usuarios'))
        
    except Exception as e:
        flash(f'❌ Erro ao excluir usuário: {str(e)}', 'error')
        return redirect(url_for('admin_usuarios'))

@app.route('/admin/relatorios')
@admin_required
def admin_relatorios():
    """Página principal de relatórios do admin"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Estatísticas gerais
        cursor.execute("SELECT COUNT(*) FROM users")
        total_usuarios = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM turmas")
        total_turmas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM aulas")
        total_aulas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM exercicios")
        total_exercicios = cursor.fetchone()[0]
        
        # Progresso por disciplina
        cursor.execute("""
            SELECT 
                d.nome as disciplina,
                COUNT(DISTINCT p.aluno_id) as alunos_ativos,
                AVG(p.pontuacao) as media_pontuacao
            FROM disciplinas d
            LEFT JOIN aulas a ON d.nome = a.disciplina
            LEFT JOIN progresso p ON a.id = p.aula_id
            WHERE p.pontuacao IS NOT NULL
            GROUP BY d.id, d.nome
            ORDER BY media_pontuacao DESC
        """)
        progresso_disciplinas = cursor.fetchall()
        
        # Usuários por tipo
        cursor.execute("""
            SELECT user_type, COUNT(*) as total
            FROM users
            GROUP BY user_type
            ORDER BY total DESC
        """)
        usuarios_por_tipo = cursor.fetchall()
        
        return render_template('admin_relatorios.html',
                             total_usuarios=total_usuarios,
                             total_turmas=total_turmas,
                             total_aulas=total_aulas,
                             total_exercicios=total_exercicios,
                             progresso_disciplinas=progresso_disciplinas,
                             usuarios_por_tipo=usuarios_por_tipo)
                             
    except Exception as e:
        flash(f'❌ Erro ao carregar relatórios: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/relatorios/usuarios')
@admin_required
def admin_relatorio_usuarios():
    """Relatório detalhado de usuários"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Usuários com estatísticas
        cursor.execute("""
            SELECT 
                u.id, u.username, u.email, u.user_type, u.created_at,
                u.first_name, u.last_name,
                CASE 
                    WHEN u.user_type = 'aluno' THEN (
                        SELECT COUNT(*) FROM aluno_turma at 
                        WHERE at.aluno_id = u.id AND (at.status = 'ativo' OR at.status IS NULL)
                    )
                    WHEN u.user_type = 'professor' THEN (
                        SELECT COUNT(*) FROM turmas t 
                        WHERE t.professor_id = u.id
                    )
                    ELSE 0
                END as contador,
                CASE 
                    WHEN u.user_type = 'aluno' THEN (
                        SELECT AVG(p.pontuacao) FROM progresso p 
                        WHERE p.aluno_id = u.id AND p.pontuacao IS NOT NULL
                    )
                    ELSE NULL
                END as media_progresso
            FROM users u
            ORDER BY u.created_at DESC
        """)
        usuarios = cursor.fetchall()
        
        return render_template('admin_relatorio_usuarios.html', usuarios=usuarios)
        
    except Exception as e:
        flash(f'❌ Erro ao carregar relatório: {str(e)}', 'error')
        return redirect(url_for('admin_relatorios'))

@app.route('/admin/relatorios/turmas')
@admin_required
def admin_relatorio_turmas():
    """Relatório detalhado de turmas"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Turmas com estatísticas
        cursor.execute("""
            SELECT 
                t.id, t.nome, t.serie, t.created_at,
                u.username as professor,
                COUNT(at.aluno_id) as total_alunos,
                COUNT(a.id) as total_aulas,
                AVG(p.pontuacao) as media_progresso
            FROM turmas t
            JOIN users u ON t.professor_id = u.id
            LEFT JOIN aluno_turma at ON t.id = at.turma_id AND (at.status = 'ativo' OR at.status IS NULL)
            LEFT JOIN aulas a ON t.serie = a.serie AND t.professor_id = a.professor_id
            LEFT JOIN progresso p ON a.id = p.aula_id
            GROUP BY t.id, t.nome, t.serie, t.created_at, u.username
            ORDER BY t.created_at DESC
        """)
        turmas = cursor.fetchall()
        
        return render_template('admin_relatorio_turmas.html', turmas=turmas)
        
    except Exception as e:
        flash(f'❌ Erro ao carregar relatório: {str(e)}', 'error')
        return redirect(url_for('admin_relatorios'))

# =====================================================
# ROTAS DE ERRO
# =====================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

# =====================================================
# FUNÇÕES AUXILIARES PARA TEMPLATES
# =====================================================

@app.context_processor
def utility_processor():
    """Funções auxiliares disponíveis em todos os templates"""
    def format_datetime(value, format='%d/%m/%Y %H:%M'):
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except:
                return value
        return value.strftime(format)
    
    def get_user_type_display(user_type):
        types = {
            'admin': '👨‍💼 Administrador',
            'professor': '👨‍🏫 Professor',
            'aluno': '👨‍🎓 Aluno'
        }
        return types.get(user_type, user_type)
    
    def get_status_display(status):
        status_map = {
            'nao_iniciado': '⏳ Não iniciado',
            'em_andamento': '▶️ Em andamento',
            'concluido': '✅ Concluído',
            'ativo': '✅ Ativo',
            'inativo': '❌ Inativo'
        }
        return status_map.get(status, status)
    
    return {
        'format_datetime': format_datetime,
        'get_user_type_display': get_user_type_display,
        'get_status_display': get_status_display
    }

# =====================================================
# SISTEMA DE GAMIFICAÇÃO
# =====================================================

@app.route('/student/gamificacao')
@aluno_required
def student_gamificacao():
    """Dashboard principal de gamificação do aluno"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Buscar informações do nível atual
        cursor.execute("""
            SELECT nivel_atual, pontos_totais, pontos_nivel_atual, pontos_proximo_nivel, 
                   titulo_nivel, cor_nivel, icone_nivel
            FROM niveis_aluno 
            WHERE aluno_id = ?
        """, (current_user.id,))
        nivel_info = cursor.fetchone()
        
        if not nivel_info:
            # Criar nível inicial se não existir
            cursor.execute("""
                INSERT INTO niveis_aluno (aluno_id, nivel_atual, pontos_totais, pontos_nivel_atual, 
                                        pontos_proximo_nivel, titulo_nivel, cor_nivel, icone_nivel)
                VALUES (?, 1, 0, 0, 100, 'Iniciante', '#6c757d', 'fas fa-star')
            """, (current_user.id,))
            db.commit()
            
            cursor.execute("""
                SELECT nivel_atual, pontos_totais, pontos_nivel_atual, pontos_proximo_nivel, 
                       titulo_nivel, cor_nivel, icone_nivel
                FROM niveis_aluno 
                WHERE aluno_id = ?
            """, (current_user.id,))
            nivel_info = cursor.fetchone()
        
        # Buscar metas semanais ativas
        cursor.execute("""
            SELECT m.id, m.nome, m.descricao, m.tipo, m.valor_meta, m.pontos_recompensa, 
                   m.recompensa_virtual, m.data_inicio, m.data_fim,
                   COALESCE(pm.valor_atual, 0) as valor_atual,
                   COALESCE(pm.concluida, 0) as concluida,
                   COALESCE(pm.recompensa_coletada, 0) as recompensa_coletada
            FROM metas_semanais m
            LEFT JOIN progresso_metas pm ON m.id = pm.meta_id AND pm.aluno_id = ?
            WHERE m.ativa = 1 AND m.data_fim >= date('now')
            ORDER BY m.data_fim ASC
        """, (current_user.id,))
        metas_semanais = cursor.fetchall() or []
        
        # Buscar conquistas recentes
        cursor.execute("""
            SELECT c.nome, c.descricao, c.pontos, c.icone, ac.data_conquista
            FROM aluno_conquista ac
            JOIN conquistas c ON ac.conquista_id = c.id
            WHERE ac.aluno_id = ?
            ORDER BY ac.data_conquista DESC
            LIMIT 5
        """, (current_user.id,))
        conquistas_recentes = cursor.fetchall() or []
        
        # Buscar histórico de pontos da semana
        cursor.execute("""
            SELECT pontos, tipo, descricao, data_ganho
            FROM historico_pontos
            WHERE aluno_id = ? AND data_ganho >= date('now', 'weekday 0', '-6 days')
            ORDER BY data_ganho DESC
            LIMIT 10
        """, (current_user.id,))
        historico_semana = cursor.fetchall() or []
        
        # Calcular progresso do nível
        progresso_nivel = 0
        if nivel_info and len(nivel_info) >= 4:
            try:
                pontos_totais = float(nivel_info[2]) if nivel_info[2] is not None else 0
                pontos_proximo = float(nivel_info[3]) if nivel_info[3] is not None else 100
                if pontos_proximo > 0:
                    progresso_nivel = (pontos_totais / pontos_proximo) * 100
            except (TypeError, ValueError, ZeroDivisionError):
                progresso_nivel = 0
        
        # Garantir que todas as variáveis são listas
        if not isinstance(metas_semanais, list):
            metas_semanais = []
        if not isinstance(conquistas_recentes, list):
            conquistas_recentes = []
        if not isinstance(historico_semana, list):
            historico_semana = []
        
        cursor.close()
        
        return render_template('student_gamificacao.html',
                             nivel_info=nivel_info,
                             metas_semanais=metas_semanais,
                             conquistas_recentes=conquistas_recentes,
                             historico_semana=historico_semana,
                             progresso_nivel=progresso_nivel)
                             
    except Exception as e:
        flash(f'❌ Erro ao carregar gamificação: {str(e)}', 'error')
        return redirect(url_for('student_dashboard'))

@app.route('/student/ranking')
@aluno_required
def student_ranking():
    """Ranking dos alunos por turma"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Buscar turmas do aluno
        cursor.execute("""
            SELECT t.id, t.nome, t.serie
            FROM aluno_turma at
            JOIN turmas t ON at.turma_id = t.id
            WHERE at.aluno_id = ? AND (at.status = 'ativo' OR at.status IS NULL)
        """, (current_user.id,))
        turmas = cursor.fetchall()
        
        # Buscar ranking da semana atual para cada turma
        rankings = []
        if isinstance(turmas, list):
            for turma in turmas:
                cursor.execute("""
                    SELECT u.username, u.first_name, u.last_name, 
                           COALESCE(rs.pontos_semana, 0) as pontos_semana,
                           COALESCE(rs.posicao, 0) as posicao
                    FROM users u
                    JOIN aluno_turma at ON u.id = at.aluno_id
                    LEFT JOIN ranking_semanal rs ON u.id = rs.aluno_id AND rs.turma_id = ?
                    WHERE at.turma_id = ? AND (at.status = 'ativo' OR at.status IS NULL)
                    ORDER BY pontos_semana DESC, u.first_name ASC
                """, (turma[0], turma[0]))
                
                ranking_turma = cursor.fetchall()
                rankings.append({
                    'turma': turma,
                    'alunos': ranking_turma
                })
        
        cursor.close()
        
        return render_template('student_ranking.html', rankings=rankings)
        
    except Exception as e:
        flash(f'❌ Erro ao carregar ranking: {str(e)}', 'error')
        return redirect(url_for('student_dashboard'))

@app.route('/student/metas')
@aluno_required
def student_metas():
    """Página detalhada de metas semanais"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Buscar todas as metas (ativas e inativas)
        cursor.execute("""
            SELECT m.id, m.nome, m.descricao, m.tipo, m.valor_meta, m.pontos_recompensa, 
                   m.recompensa_virtual, m.data_inicio, m.data_fim, m.ativa,
                   COALESCE(pm.valor_atual, 0) as valor_atual,
                   COALESCE(pm.concluida, 0) as concluida,
                   COALESCE(pm.recompensa_coletada, 0) as recompensa_coletada,
                   COALESCE(pm.data_conclusao, '') as data_conclusao
            FROM metas_semanais m
            LEFT JOIN progresso_metas pm ON m.id = pm.meta_id AND pm.aluno_id = ?
            ORDER BY m.data_inicio DESC
        """, (current_user.id,))
        todas_metas = cursor.fetchall()
        
        # Garantir que todas_metas é uma lista
        if not isinstance(todas_metas, list):
            todas_metas = []
        
        # Calcular estatísticas
        metas_concluidas = len([m for m in todas_metas if m[11] == 1])
        total_metas = len(todas_metas)
        pontos_ganhos = sum([m[5] for m in todas_metas if m[11] == 1 and m[12] == 1])
        
        cursor.close()
        
        return render_template('student_metas.html',
                             todas_metas=todas_metas,
                             metas_concluidas=metas_concluidas,
                             total_metas=total_metas,
                             pontos_ganhos=pontos_ganhos)
                             
    except Exception as e:
        flash(f'❌ Erro ao carregar metas: {str(e)}', 'error')
        return redirect(url_for('student_dashboard'))

@app.route('/student/conquistas')
@aluno_required
def student_conquistas():
    """Página de conquistas do aluno"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Buscar conquistas já obtidas
        cursor.execute("""
            SELECT c.id, c.nome, c.descricao, c.pontos, c.icone, ac.data_conquista
            FROM aluno_conquista ac
            JOIN conquistas c ON ac.conquista_id = c.id
            WHERE ac.aluno_id = ?
            ORDER BY ac.data_conquista DESC
        """, (current_user.id,))
        conquistas_obtidas = cursor.fetchall()
        
        # Buscar todas as conquistas disponíveis
        cursor.execute("""
            SELECT id, nome, descricao, pontos, icone, criterio
            FROM conquistas
            ORDER BY pontos ASC
        """)
        todas_conquistas = cursor.fetchall()
        
        # Garantir que as variáveis são listas
        if not isinstance(conquistas_obtidas, list):
            conquistas_obtidas = []
        if not isinstance(todas_conquistas, list):
            todas_conquistas = []
        
        # Calcular progresso das conquistas
        conquistas_progresso = []
        for conquista in todas_conquistas:
            # Verificar se já foi obtida
            obtida = any(c[0] == conquista[0] for c in conquistas_obtidas)
            
            # Calcular progresso baseado no critério
            progresso = 0
            if conquista[5]:  # se tem critério
                if conquista[5] == 'primeira_aula':
                    cursor.execute("""
                        SELECT COUNT(*) FROM progresso 
                        WHERE aluno_id = ? AND status != 'nao_iniciado'
                    """, (current_user.id,))
                    progresso = min(cursor.fetchone()[0], 1)
                elif conquista[5] == 'cinco_aulas':
                    cursor.execute("""
                        SELECT COUNT(*) FROM progresso 
                        WHERE aluno_id = ? AND status = 'concluido'
                    """, (current_user.id,))
                    progresso = min(cursor.fetchone()[0], 5)
                elif conquista[5] == 'vinte_aulas':
                    cursor.execute("""
                        SELECT COUNT(*) FROM progresso 
                        WHERE aluno_id = ? AND status = 'concluido'
                    """, (current_user.id,))
                    progresso = min(cursor.fetchone()[0], 20)
            
            conquistas_progresso.append({
                'conquista': conquista,
                'obtida': obtida,
                'progresso': progresso
            })
        
        cursor.close()
        
        return render_template('student_conquistas.html',
                             conquistas_obtidas=conquistas_obtidas,
                             conquistas_progresso=conquistas_progresso)
                             
    except Exception as e:
        flash(f'❌ Erro ao carregar conquistas: {str(e)}', 'error')
        return redirect(url_for('student_dashboard'))

@app.route('/student/coletar-recompensa/<int:meta_id>', methods=['POST'])
@aluno_required
def coletar_recompensa(meta_id):
    """Coletar recompensa de uma meta concluída"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Verificar se a meta foi concluída e a recompensa não foi coletada
        cursor.execute("""
            SELECT m.pontos_recompensa, m.recompensa_virtual, pm.concluida, pm.recompensa_coletada
            FROM metas_semanais m
            JOIN progresso_metas pm ON m.id = pm.meta_id
            WHERE m.id = ? AND pm.aluno_id = ?
        """, (meta_id, current_user.id))
        
        meta = cursor.fetchone()
        if not meta:
            flash('❌ Meta não encontrada.', 'error')
            return redirect(url_for('student_metas'))
        
        if not meta[2]:  # não concluída
            flash('❌ Meta ainda não foi concluída.', 'error')
            return redirect(url_for('student_metas'))
        
        if meta[3]:  # recompensa já coletada
            flash('❌ Recompensa já foi coletada.', 'error')
            return redirect(url_for('student_metas'))
        
        # Coletar recompensa
        cursor.execute("""
            UPDATE progresso_metas 
            SET recompensa_coletada = 1 
            WHERE meta_id = ? AND aluno_id = ?
        """, (meta_id, current_user.id))
        
        # Adicionar pontos ao histórico
        cursor.execute("""
            INSERT INTO historico_pontos (aluno_id, pontos, tipo, descricao, referencia_id, referencia_tipo)
            VALUES (?, ?, 'meta', 'Recompensa de meta semanal', ?, 'meta')
        """, (current_user.id, meta[0], meta_id))
        
        # Atualizar pontos totais
        cursor.execute("""
            UPDATE niveis_aluno 
            SET pontos_totais = pontos_totais + ?
            WHERE aluno_id = ?
        """, (meta[0], current_user.id))
        
        db.commit()
        cursor.close()
        
        flash(f'✅ Recompensa coletada! +{meta[0]} pontos e {meta[1]}', 'success')
        return redirect(url_for('student_metas'))
        
    except Exception as e:
        flash(f'❌ Erro ao coletar recompensa: {str(e)}', 'error')
        return redirect(url_for('student_metas'))

# =====================================================
# FUNÇÕES AUXILIARES DE GAMIFICAÇÃO
# =====================================================

def atualizar_progresso_metas(aluno_id, tipo, valor=1):
    """Atualizar progresso das metas semanais de um aluno"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Buscar metas ativas do tipo especificado
        cursor.execute("""
            SELECT id, valor_meta, pontos_recompensa
            FROM metas_semanais
            WHERE tipo = ? AND ativa = 1 AND data_fim >= date('now')
        """, (tipo,))
        
        metas = cursor.fetchall()
        
        for meta in metas:
            meta_id = meta[0]
            valor_meta = meta[1]
            pontos_recompensa = meta[2]
            
            # Buscar ou criar progresso da meta
            cursor.execute("""
                SELECT id, valor_atual, concluida
                FROM progresso_metas
                WHERE meta_id = ? AND aluno_id = ?
            """, (meta_id, aluno_id))
            
            progresso = cursor.fetchone()
            
            if progresso:
                # Atualizar progresso existente
                novo_valor = progresso[1] + valor
                concluida = novo_valor >= valor_meta
                
                cursor.execute("""
                    UPDATE progresso_metas
                    SET valor_atual = ?, concluida = ?, 
                        data_conclusao = CASE WHEN ? AND concluida = 0 THEN CURRENT_TIMESTAMP ELSE data_conclusao END
                    WHERE id = ?
                """, (novo_valor, concluida, concluida, progresso[0]))
            else:
                # Criar novo progresso
                novo_valor = valor
                concluida = novo_valor >= valor_meta
                
                cursor.execute("""
                    INSERT INTO progresso_metas (aluno_id, meta_id, valor_atual, concluida, data_conclusao)
                    VALUES (?, ?, ?, ?, CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE NULL END)
                """, (aluno_id, meta_id, novo_valor, concluida, concluida))
            
            # Se a meta foi concluída, mostrar notificação
            if concluida and not progresso or (progresso and not progresso[2]):
                flash(f'🎯 Meta "{tipo}" concluída! Recompensa disponível.', 'success')
        
        db.commit()
        cursor.close()
        
    except Exception as e:
        print(f"Erro ao atualizar progresso de metas: {e}")

def verificar_conquistas(aluno_id):
    """Verificar e conceder conquistas automaticamente"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Verificar conquista "Primeiro Passo"
        cursor.execute("""
            SELECT COUNT(*) FROM progresso 
            WHERE aluno_id = ? AND status != 'nao_iniciado'
        """, (aluno_id,))
        aulas_iniciadas = cursor.fetchone()[0]
        
        if aulas_iniciadas >= 1:
            cursor.execute("""
                SELECT id FROM conquistas WHERE nome = 'Primeiro Passo'
            """)
            conquista = cursor.fetchone()
            
            if conquista:
                # Verificar se já tem a conquista
                cursor.execute("""
                    SELECT id FROM aluno_conquista 
                    WHERE aluno_id = ? AND conquista_id = ?
                """, (aluno_id, conquista[0]))
                
                if not cursor.fetchone():
                    # Conceder conquista
                    cursor.execute("""
                        INSERT INTO aluno_conquista (aluno_id, conquista_id)
                        VALUES (?, ?)
                    """, (aluno_id, conquista[0]))
                    
                    # Adicionar pontos
                    cursor.execute("""
                        INSERT INTO historico_pontos (aluno_id, pontos, tipo, descricao, referencia_id, referencia_tipo)
                        VALUES (?, 50, 'conquista', 'Conquista: Primeiro Passo', ?, 'conquista')
                    """, (aluno_id, conquista[0]))
                    
                    flash('🏆 Nova conquista desbloqueada: Primeiro Passo! +50 pontos', 'success')
        
        # Verificar conquista "Estudante Dedicado"
        cursor.execute("""
            SELECT COUNT(*) FROM progresso 
            WHERE aluno_id = ? AND status = 'concluido'
        """, (aluno_id,))
        aulas_concluidas = cursor.fetchone()[0]
        
        if aulas_concluidas >= 5:
            cursor.execute("""
                SELECT id FROM conquistas WHERE nome = 'Estudante Dedicado'
            """)
            conquista = cursor.fetchone()
            
            if conquista:
                cursor.execute("""
                    SELECT id FROM aluno_conquista 
                    WHERE aluno_id = ? AND conquista_id = ?
                """, (aluno_id, conquista[0]))
                
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO aluno_conquista (aluno_id, conquista_id)
                        VALUES (?, ?)
                    """, (aluno_id, conquista[0]))
                    
                    cursor.execute("""
                        INSERT INTO historico_pontos (aluno_id, pontos, tipo, descricao, referencia_id, referencia_tipo)
                        VALUES (?, 100, 'conquista', 'Conquista: Estudante Dedicado', ?, 'conquista')
                    """, (aluno_id, conquista[0]))
                    
                    flash('🏆 Nova conquista desbloqueada: Estudante Dedicado! +100 pontos', 'success')
        
        db.commit()
        cursor.close()
        
    except Exception as e:
        print(f"Erro ao verificar conquistas: {e}")

def atualizar_nivel_aluno(aluno_id):
    """Atualizar nível do aluno baseado nos pontos totais"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Buscar pontos totais
        cursor.execute("""
            SELECT COALESCE(SUM(pontos), 0) as pontos_totais
            FROM historico_pontos
            WHERE aluno_id = ?
        """, (aluno_id,))
        
        pontos_totais = cursor.fetchone()[0]
        
        # Calcular nível (cada nível requer 100 pontos)
        nivel_atual = (pontos_totais // 100) + 1
        pontos_nivel_atual = pontos_totais % 100
        pontos_proximo_nivel = 100
        
        # Definir título e cor do nível
        if nivel_atual == 1:
            titulo = 'Iniciante'
            cor = '#6c757d'
            icone = 'fas fa-star'
        elif nivel_atual == 2:
            titulo = 'Aprendiz'
            cor = '#28a745'
            icone = 'fas fa-star'
        elif nivel_atual == 3:
            titulo = 'Estudante'
            cor = '#007bff'
            icone = 'fas fa-star'
        elif nivel_atual == 4:
            titulo = 'Avançado'
            cor = '#6f42c1'
            icone = 'fas fa-star'
        elif nivel_atual == 5:
            titulo = 'Mestre'
            cor = '#fd7e14'
            icone = 'fas fa-crown'
        else:
            titulo = f'Nível {nivel_atual}'
            cor = '#dc3545'
            icone = 'fas fa-crown'
        
        # Atualizar ou inserir nível
        cursor.execute("""
            INSERT OR REPLACE INTO niveis_aluno 
            (aluno_id, nivel_atual, pontos_totais, pontos_nivel_atual, pontos_proximo_nivel, 
             titulo_nivel, cor_nivel, icone_nivel, ultima_atualizacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (aluno_id, nivel_atual, pontos_totais, pontos_nivel_atual, pontos_proximo_nivel, 
               titulo, cor, icone))
        
        db.commit()
        cursor.close()
        
    except Exception as e:
        print(f"Erro ao atualizar nível: {e}")

# =====================================================
# ATUALIZAR ROTAS EXISTENTES PARA INTEGRAR GAMIFICAÇÃO
# =====================================================

# Atualizar a rota de fazer exercício para incluir gamificação
@app.route('/student/exercicio/<int:exercicio_id>', methods=['GET', 'POST'])
@aluno_required
def fazer_exercicio(exercicio_id):
    """Fazer exercício específico com sistema de gamificação"""
    db = get_db()
    
    if request.method == 'POST':
        resposta_aluno = request.form.get('resposta')
        
        # Buscar exercício
        cur = db.cursor()
        cur.execute('''
            SELECT e.id, e.enunciado, e.alternativas, e.resposta_correta, e.aula_id, e.pontos,
                   a.titulo
            FROM exercicios e
            JOIN aulas a ON e.aula_id = a.id
            WHERE e.id = ?
        ''', (exercicio_id,))
        exercicio = cur.fetchone()
        
        if not exercicio:
            flash('❌ Exercício não encontrado.', 'error')
            return redirect(url_for('student_aulas'))
        
        # Verificar resposta
        correto = resposta_aluno == exercicio[3]
        pontos_exercicio = exercicio[4] if correto else 0
        
        # Atualizar progresso
        try:
            cur.execute('''
                INSERT OR REPLACE INTO progresso (aluno_id, aula_id, status, pontuacao, ultima_atividade)
                VALUES (?, ?, 'em_andamento', ?, CURRENT_TIMESTAMP)
            ''', (current_user.id, exercicio[4], pontos_exercicio))
            
            # Se acertou, adicionar pontos ao histórico e atualizar gamificação
            if correto:
                # Adicionar ao histórico de pontos
                cur.execute('''
                    INSERT INTO historico_pontos (aluno_id, pontos, tipo, descricao, referencia_id, referencia_tipo)
                    VALUES (?, ?, 'exercicio', ?, ?, 'exercicio')
                ''', (current_user.id, pontos_exercicio, f'Exercício correto: {exercicio[6]}', exercicio_id))
                
                # Atualizar progresso de metas
                atualizar_progresso_metas(current_user.id, 'exercicios')
                
                # Verificar conquistas
                verificar_conquistas(current_user.id)
                
                # Atualizar nível
                atualizar_nivel_aluno(current_user.id)
                
                flash(f'✅ Resposta correta! +{pontos_exercicio} pontos!', 'success')
            else:
                flash(f'❌ Resposta incorreta. A resposta correta era: {exercicio[3]}', 'error')
                
        except Exception as e:
            flash(f'❌ Erro ao salvar progresso: {str(e)}', 'error')
        
        cur.close()
        
        return redirect(url_for('fazer_exercicio', exercicio_id=exercicio_id))
    
    # GET: mostrar exercício
    cur = db.cursor()
    cur.execute('''
        SELECT e.id, e.enunciado, e.alternativas, e.resposta_correta, e.aula_id,
               a.titulo, a.disciplina, e.pontos
        FROM exercicios e
        JOIN aulas a ON e.aula_id = a.id
        WHERE e.id = ?
    ''', (exercicio_id,))
    exercicio = cur.fetchone()
    
    if not exercicio:
        flash('❌ Exercício não encontrado.', 'error')
        return redirect(url_for('student_aulas'))
    
    # Converter alternativas de string para lista
    alternativas = exercicio[2].split('|') if exercicio[2] else []
    
    cur.close()
    
    return render_template('student_exercicio.html', 
                         exercicio=exercicio, 
                         alternativas=alternativas)

# Atualizar a rota de concluir aula para incluir gamificação
@app.route('/student/aula/<int:aula_id>/concluir', methods=['POST'])
@aluno_required
def concluir_aula(aula_id):
    """Concluir uma aula com sistema de gamificação"""
    db = get_db()
    
    try:
        cur = db.cursor()
        cur.execute('''
            UPDATE progresso 
            SET status = 'concluido', ultima_atividade = CURRENT_TIMESTAMP
            WHERE aluno_id = ? AND aula_id = ?
        ''', (current_user.id, aula_id))
        
        # Adicionar pontos por concluir aula
        pontos_aula = 25
        cur.execute('''
            INSERT INTO historico_pontos (aluno_id, pontos, tipo, descricao, referencia_id, referencia_tipo)
            VALUES (?, ?, 'aula', 'Aula concluída', ?, 'aula')
        ''', (current_user.id, pontos_aula, aula_id))
        
        # Atualizar progresso de metas
        atualizar_progresso_metas(current_user.id, 'aulas')
        
        # Verificar conquistas
        verificar_conquistas(current_user.id)
        
        # Atualizar nível
        atualizar_nivel_aluno(current_user.id)
        
        db.commit()
        cur.close()
        
        flash(f'🎉 Parabéns! Aula concluída com sucesso! +{pontos_aula} pontos', 'success')
    except Exception as e:
        flash(f'❌ Erro ao concluir aula: {str(e)}', 'error')
    
    return redirect(url_for('student_aula_view', aula_id=aula_id))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
