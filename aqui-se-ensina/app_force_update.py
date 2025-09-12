from flask import Flask, render_template, redirect, url_for, flash, request, session
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configurações da aplicação
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

@app.route('/')
def splash():
    """Página inicial da aplicação - FORCE UPDATE"""
    return '''
    <h1>🚀 Escola para Todos V2 - FORCE UPDATE</h1>
    <p>✅ Esta é a versão SEM BANCO funcionando no Render!</p>
    <p>🎯 Status: ONLINE e ATUALIZADO</p>
    <p>🔧 Versão: app_no_db.py</p>
    <p>📅 Deploy: 26/08/2025 - Commit bcdba0f</p>
    <hr>
    <p><a href="/login">🔐 Fazer Login</a></p>
    <p><a href="/admin/dashboard">📊 Dashboard Admin</a></p>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login simplificada"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Login temporário para teste
        if username == 'admin' and password == 'admin123':
            session['user_id'] = 1
            session['username'] = 'admin'
            session['user_type'] = 'admin'
            flash('✅ Login realizado com sucesso!', 'info')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('❌ Username ou senha incorretos.', 'error')
    
    return render_template('login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Dashboard administrativo"""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    return render_template('admin_dashboard.html')

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('👋 Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('splash'))

@app.route('/health')
def health():
    """Health check para o Render"""
    return 'OK - FORCE UPDATE', 200

@app.route('/version')
def version():
    """Verificar versão"""
    return 'app_force_update.py - Commit bcdba0f - Render Online! 🚀'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
