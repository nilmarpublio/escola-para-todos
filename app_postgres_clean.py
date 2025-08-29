from flask import Flask, render_template, redirect, url_for, flash, request, session, g, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg
import os
from datetime import datetime, timedelta
from auth import admin_required, professor_required, aluno_required
from models_postgres import User, get_db

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        cur.close()
        
        if user_data:
            return User(user_data)
        return None
    except Exception as e:
        print(f"Erro ao carregar usuário: {e}")
        return None

@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_data = cur.fetchone()
            cur.close()
            
            if user_data and check_password_hash(user_data['password'], password):
                user = User(user_data)
                login_user(user)
                
                if user.is_admin:
                    return redirect(url_for('admin_dashboard'))
                elif user.is_professor:
                    return redirect(url_for('professor_dashboard'))
                elif user.is_aluno:
                    return redirect(url_for('student_dashboard'))
                else:
                    flash('❌ Tipo de usuário não reconhecido!', 'error')
                    return redirect(url_for('login'))
            else:
                flash('❌ Usuário ou senha incorretos!', 'error')
                
        except Exception as e:
            print(f"Erro no login: {e}")
            flash('❌ Erro interno do sistema!', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('✅ Logout realizado com sucesso!', 'success')
    return redirect(url_for('splash'))

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    try:
        db = get_db()
        cur = db.cursor()
        
        # Estatísticas básicas
        cur.execute("SELECT COUNT(*) as total FROM users WHERE user_type = 'aluno'")
        total_alunos = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as total FROM users WHERE user_type = 'professor'")
        total_professores = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as total FROM turmas")
        total_turmas = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as total FROM aulas")
        total_aulas = cur.fetchone()['total']
        
        stats = [total_alunos, total_professores, total_turmas, total_aulas]
        cur.close()
        
        return render_template('admin_dashboard.html', stats=stats)
        
    except Exception as e:
        print(f"Erro no admin dashboard: {e}")
        flash('❌ Erro ao carregar dashboard!', 'error')
        return render_template('admin_dashboard.html', stats=[0, 0, 0, 0])

@app.route('/professor/dashboard')
@login_required
@professor_required
def professor_dashboard():
    return render_template('professor_dashboard.html')

@app.route('/student/dashboard')
@login_required
@aluno_required
def student_dashboard():
    """Dashboard principal do aluno"""
    try:
        print(f"🔍 DEBUG: ===== STUDENT DASHBOARD INICIADO =====")
        print(f"🔍 DEBUG: Usuário ID: {current_user.id}")
        print(f"🔍 DEBUG: Usuário Type: {current_user.user_type}")
        print(f"🔍 DEBUG: is_aluno: {current_user.is_aluno}")
        
        db = get_db()
        cur = db.cursor()
        
        # Estatísticas do aluno
        try:
            cur.execute("""
                SELECT 
                    COUNT(*) as total_aulas,
                    COUNT(CASE WHEN pa.status = 'concluida' THEN 1 END) as aulas_concluidas,
                    COUNT(CASE WHEN pa.status = 'em_progresso' THEN 1 END) as aulas_em_progresso,
                    COALESCE(SUM(pa.pontos_ganhos), 0) as total_pontos
                FROM aulas a
                LEFT JOIN progresso_alunos pa ON a.id = pa.aula_id AND pa.aluno_id = %s
                WHERE a.is_active = true
            """, (current_user.id,))
            
            stats = cur.fetchone()
            print(f"🔍 DEBUG: Stats: {stats}")
            
        except Exception as e:
            print(f"❌ Erro na query de estatísticas: {e}")
            stats = {'total_aulas': 0, 'aulas_concluidas': 0, 'aulas_em_progresso': 0, 'total_pontos': 0}
        
        # Turmas matriculadas
        try:
            cur.execute("""
                SELECT t.nome, t.descricao, 
                       COUNT(a.id) as total_aulas,
                       COUNT(CASE WHEN pa.status = 'concluida' THEN 1 END) as aulas_concluidas
                FROM turmas t
                JOIN turmas_alunos ta ON t.id = ta.turma_id
                LEFT JOIN aulas a ON t.id = a.turma_id
                LEFT JOIN progresso_alunos pa ON a.id = pa.aula_id AND pa.aluno_id = %s
                WHERE ta.aluno_id = %s AND t.is_active = true
                GROUP BY t.id, t.nome, t.descricao
            """, (current_user.id, current_user.id))
            
            turmas = cur.fetchall()
            print(f"🔍 DEBUG: Turmas: {len(turmas)} encontradas")
            
        except Exception as e:
            print(f"❌ Erro na query de turmas: {e}")
            turmas = []
        
        # Aulas recentes
        try:
            cur.execute("""
                SELECT a.titulo, a.descricao, a.duracao, a.nivel_dificuldade,
                       COALESCE(pa.status, 'não iniciada') as status,
                       COALESCE(pa.pontos_ganhos, 0) as pontos
                FROM aulas a
                LEFT JOIN progresso_alunos pa ON a.id = pa.aula_id AND pa.aluno_id = %s
                WHERE a.is_active = true
                ORDER BY a.created_at DESC
                LIMIT 5
            """, (current_user.id,))
            
            aulas_recentes = cur.fetchall()
            print(f"🔍 DEBUG: Aulas recentes: {len(aulas_recentes)} encontradas")
            
        except Exception as e:
            print(f"❌ Erro na query de aulas recentes: {e}")
            aulas_recentes = []
        
        cur.close()
        
        # Preparar dados para o template
        data = {
            'total_aulas': stats['total_aulas'] or 0,
            'aulas_concluidas': stats['aulas_concluidas'] or 0,
            'aulas_em_progresso': stats['aulas_em_progresso'] or 0,
            'total_pontos': stats['total_pontos'] or 0,
            'nivel_atual': 'Iniciante' if (stats['total_pontos'] or 0) < 100 else 'Intermediário' if (stats['total_pontos'] or 0) < 500 else 'Avançado',
            'turmas_matriculadas': turmas,
            'aulas_recentes': aulas_recentes
        }
        
        print(f"🔍 DEBUG: Dados preparados: {data}")
        print(f"🔍 DEBUG: ===== STUDENT DASHBOARD FINALIZADO =====")
        
        return render_template('student_dashboard.html', data=data)
        
    except Exception as e:
        print(f"❌ ERRO GERAL no student_dashboard: {e}")
        flash('❌ Erro ao carregar dashboard!', 'error')
        return render_template('student_dashboard.html', data={
            'total_aulas': 0,
            'aulas_concluidas': 0,
            'aulas_em_progresso': 0,
            'total_pontos': 0,
            'nivel_atual': 'Iniciante',
            'turmas_matriculadas': [],
            'aulas_recentes': []
        })

@app.route('/student/educacao-basica')
@login_required
@aluno_required
def kids_dashboard():
    """Dashboard para educação básica"""
    try:
        db = get_db()
        cur = db.cursor()
        
        # Buscar aulas para educação infantil
        cur.execute("""
            SELECT id, titulo, descricao, duracao, nivel_dificuldade
            FROM aulas
            WHERE serie IN ('infantil', 'pre-escola') AND is_active = true
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        aulas_infantil = cur.fetchall()
        cur.close()
        
        # Dados de exemplo para progresso e conquistas
        progresso_categorias = {
            'linguagem': 75,
            'matematica': 60,
            'ciencias': 45,
            'artes': 80
        }
        
        conquistas = [
            {'nome': 'Primeira Aula', 'descricao': 'Completou sua primeira aula', 'icone': '🎯'},
            {'nome': 'Estudioso', 'descricao': 'Completou 5 aulas', 'icone': '📚'},
            {'nome': 'Persistence', 'descricao': 'Estudou por 3 dias seguidos', 'icone': '🔥'}
        ]
        
        return render_template('kids_dashboard.html', 
                             aulas_infantil=aulas_infantil, 
                             progresso_categorias=progresso_categorias, 
                             conquistas=conquistas)
                             
    except Exception as e:
        print(f"Erro no kids_dashboard: {e}")
        return render_template('kids_dashboard.html', aulas_infantil=[], progresso_categorias={}, conquistas=[])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
