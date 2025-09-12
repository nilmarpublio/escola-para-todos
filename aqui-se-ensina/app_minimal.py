from flask import Flask, jsonify
import os

app = Flask(__name__)
app.secret_key = 'minimal-key'

@app.route('/')
def home():
    return jsonify({
        'status': 'working',
        'message': 'Aplicação mínima funcionando no Render!',
        'environment': os.getenv('FLASK_ENV', 'unknown'),
        'database_url': 'set' if os.getenv('DATABASE_URL') else 'not set'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/test-db')
def test_db():
    try:
        import psycopg
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            return jsonify({'database': 'psycopg disponível', 'url': 'configurada'})
        else:
            return jsonify({'database': 'psycopg disponível', 'url': 'não configurada'})
    except ImportError:
        return jsonify({'database': 'psycopg não disponível'})

@app.route('/test-imports')
def test_imports():
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
    
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
