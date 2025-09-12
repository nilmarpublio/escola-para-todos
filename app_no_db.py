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
    """Página inicial da aplicação"""
    return render_template('splash.html')

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
            flash('✅ Login realizado com sucesso!', 'success')
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
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
