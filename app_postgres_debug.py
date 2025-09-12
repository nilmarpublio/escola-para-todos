from flask import Flask, render_template, redirect, url_for, flash, request, session, g, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import traceback
import sys

# Configuração básica sem imports problemáticos
app = Flask(__name__)
app.secret_key = 'debug-key'

@app.route('/')
def splash():
    """Página inicial da aplicação"""
    try:
        return render_template('splash.html')
    except Exception as e:
        return f'Erro no template splash.html: {str(e)}<br><pre>{traceback.format_exc()}</pre>', 500

@app.route('/health')
def health():
    """Health check da aplicação"""
    return jsonify({
        'status': 'healthy',
        'message': 'Debug version working',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test-imports')
def test_imports():
    """Testar todos os imports"""
    results = {}
    
    # Testar imports básicos
    try:
        import psycopg
        results['psycopg'] = '✅ OK'
    except Exception as e:
        results['psycopg'] = f'❌ Erro: {str(e)}'
    
    try:
        from models_postgres import User
        results['models_postgres'] = '✅ OK'
    except Exception as e:
        results['models_postgres'] = f'❌ Erro: {str(e)}'
    
    try:
        from auth import admin_required
        results['auth'] = '✅ OK'
    except Exception as e:
        results['auth'] = f'❌ Erro: {str(e)}'
    
    try:
        from api.turmas import register_turmas_api
        results['api.turmas'] = '✅ OK'
    except Exception as e:
        results['api.turmas'] = f'❌ Erro: {str(e)}'
    
    try:
        from api.swagger import create_swagger_blueprint
        results['api.swagger'] = '✅ OK'
    except Exception as e:
        results['api.swagger'] = f'❌ Erro: {str(e)}'
    
    return jsonify(results)

@app.route('/test-db')
def test_db():
    """Testar conexão com banco"""
    try:
        import psycopg
        from psycopg.rows import dict_row
        
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            conn = psycopg.connect(database_url, row_factory=dict_row)
            cur = conn.cursor()
            cur.execute('SELECT 1 as test')
            result = cur.fetchone()
            cur.close()
            conn.close()
            return jsonify({'database': '✅ Conectado com sucesso', 'result': result})
        else:
            return jsonify({'database': '⚠️ DATABASE_URL não configurada'})
    except Exception as e:
        return jsonify({'database': f'❌ Erro: {str(e)}', 'traceback': traceback.format_exc()})

if __name__ == '__main__':
    print("🚀 Iniciando app_postgres_debug.py")
    print("📊 Versão de debug para identificar problemas")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
