from flask import Flask, render_template, redirect, url_for, flash, request, session, g, abort
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

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

def get_db():
    """Conectar ao banco de dados PostgreSQL"""
    if 'db' not in g:
        try:
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
        except Exception as e:
            print(f"Erro ao conectar ao banco: {e}")
            g.db = None
    return g.db

def close_db(e=None):
    """Fechar conexão com o banco"""
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except:
            pass

app.teardown_appcontext(close_db)

# =====================================================
# ROTAS PÚBLICAS
# =====================================================

@app.route('/')
def splash():
    """Página inicial da aplicação"""
    try:
        return render_template('splash.html')
    except Exception as e:
        return f'Erro ao carregar página: {str(e)}', 500

@app.route('/health')
def health():
    """Health check para o Render"""
    try:
        db = get_db()
        if db:
            return 'OK - Aplicação funcionando com PostgreSQL! 🚀', 200
        else:
            return 'OK - Aplicação funcionando (sem banco)! 🚀', 200
    except Exception as e:
        return f'OK - Aplicação funcionando (erro no banco: {str(e)})! 🚀', 200

@app.route('/version')
def version():
    """Verificar versão"""
    return 'app_render.py - Aplicação otimizada para Render - Online! 🎯'

@app.route('/test')
def test():
    """Página de teste"""
    return '''
    <html>
    <head><title>Teste - Escola para Todos</title></head>
    <body>
        <h1>🎓 Escola para Todos</h1>
        <h2>✅ Aplicação funcionando no Render!</h2>
        <p>Esta é uma versão simplificada para teste.</p>
        <ul>
            <li><a href="/">Página inicial</a></li>
            <li><a href="/health">Health check</a></li>
            <li><a href="/version">Versão</a></li>
        </ul>
    </body>
    </html>
    '''

# =====================================================
# ROTAS DE ERRO
# =====================================================

@app.errorhandler(404)
def not_found_error(error):
    return '''
    <html>
    <head><title>Página não encontrada</title></head>
    <body>
        <h1>404 - Página não encontrada</h1>
        <p>A página que você está procurando não existe.</p>
        <a href="/">Voltar ao início</a>
    </body>
    </html>
    ''', 404

@app.errorhandler(500)
def internal_error(error):
    return '''
    <html>
    <head><title>Erro interno</title></head>
    <body>
        <h1>500 - Erro interno do servidor</h1>
        <p>Ocorreu um erro inesperado. Tente novamente mais tarde.</p>
        <a href="/">Voltar ao início</a>
    </body>
    </html>
    ''', 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
