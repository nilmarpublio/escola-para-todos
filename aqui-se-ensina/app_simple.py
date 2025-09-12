from flask import Flask
import os

# Inicialização da aplicação
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

@app.route('/')
def home():
    """Página inicial simples"""
    return '''
    <html>
    <head>
        <title>🎓 Aqui se Ensina</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container { 
                text-align: center; 
                padding: 40px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 { font-size: 3rem; margin-bottom: 20px; }
            h2 { font-size: 1.5rem; margin-bottom: 30px; opacity: 0.9; }
            .status { 
                background: rgba(0,255,0,0.2); 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0;
                border: 2px solid rgba(0,255,0,0.3);
            }
            .links { margin-top: 30px; }
            .links a { 
                color: white; 
                text-decoration: none; 
                margin: 0 15px; 
                padding: 10px 20px;
                background: rgba(255,255,255,0.2);
                border-radius: 25px;
                transition: all 0.3s ease;
            }
            .links a:hover { 
                background: rgba(255,255,255,0.3);
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 Aqui se Ensina</h1>
            <h2>Sistema de Educação Digital</h2>
            
            <div class="status">
                <h3>✅ Status: Online e Funcionando!</h3>
                <p>Aplicação Flask rodando com sucesso no Render</p>
            </div>
            
            <div class="links">
                <a href="/health">🏥 Health Check</a>
                <a href="/version">📋 Versão</a>
                <a href="/test">🧪 Teste</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    """Health check para o Render"""
    return '''
    <html>
    <head><title>Health Check</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0;">
        <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h1 style="color: #28a745;">🏥 Health Check</h1>
            <h2 style="color: #28a745;">✅ Status: Saudável</h2>
            <p><strong>Aplicação:</strong> Aqui se Ensina</p>
            <p><strong>Status:</strong> Online e funcionando</p>
            <p><strong>Servidor:</strong> Render</p>
            <p><strong>Framework:</strong> Flask</p>
            <a href="/" style="color: #007bff;">← Voltar ao início</a>
        </div>
    </body>
    </html>
    '''

@app.route('/version')
def version():
    """Informações da versão"""
    return '''
    <html>
    <head><title>Versão</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0;">
        <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h1 style="color: #17a2b8;">📋 Informações da Versão</h1>
            <h2>app_simple.py</h2>
            <p><strong>Versão:</strong> 1.0.0</strong></p>
            <p><strong>Descrição:</strong> Versão simplificada para Render</p>
            <p><strong>Framework:</strong> Flask</p>
            <p><strong>Deploy:</strong> Render</p>
            <p><strong>Status:</strong> ✅ Funcionando</p>
            <a href="/" style="color: #007bff;">← Voltar ao início</a>
        </div>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    """Página de teste"""
    return '''
    <html>
    <head><title>Teste</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0;">
        <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h1 style="color: #ffc107;">🧪 Página de Teste</h1>
            <h2>Teste de Funcionamento</h2>
            <p>Se você está vendo esta página, a aplicação está funcionando perfeitamente!</p>
            <ul>
                <li>✅ Flask funcionando</li>
                <li>✅ Rotas respondendo</li>
                <li>✅ Render funcionando</li>
                <li>✅ Deploy bem-sucedido</li>
            </ul>
            <a href="/" style="color: #007bff;">← Voltar ao início</a>
        </div>
    </body>
    </html>
    '''

@app.errorhandler(404)
def not_found_error(error):
    return '''
    <html>
    <head><title>Página não encontrada</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0;">
        <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h1 style="color: #dc3545;">404 - Página não encontrada</h1>
            <p>A página que você está procurando não existe.</p>
            <a href="/" style="color: #007bff;">← Voltar ao início</a>
        </div>
    </body>
    </html>
    ''', 404

@app.errorhandler(500)
def internal_error(error):
    return '''
    <html>
    <head><title>Erro interno</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0;">
        <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h1 style="color: #dc3545;">500 - Erro interno do servidor</h1>
            <p>Ocorreu um erro inesperado. Tente novamente mais tarde.</p>
            <a href="/" style="color: #007bff;">← Voltar ao início</a>
        </div>
    </body>
    </html>
    ''', 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
