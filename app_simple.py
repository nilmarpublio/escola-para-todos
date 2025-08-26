from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🚀 Escola para Todos V2 - Render Test</h1>
    <p>✅ Flask está funcionando no Render!</p>
    <p>🎯 Status: ONLINE</p>
    <p>🔧 Próximo passo: Configurar aplicação completa</p>
    '''

@app.route('/health')
def health():
    return 'OK', 200

@app.route('/test')
def test():
    return 'Teste funcionando! 🎉'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
