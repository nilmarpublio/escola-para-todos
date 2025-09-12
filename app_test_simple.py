from flask import Flask, render_template
import os

app = Flask(__name__)
app.secret_key = 'test-key'

@app.route('/')
def home():
    return 'Hello World - Teste Simples!'

@app.route('/health')
def health():
    return {'status': 'healthy', 'message': 'Teste funcionando'}

@app.route('/test-template')
def test_template():
    try:
        return render_template('splash.html')
    except Exception as e:
        return f'Erro no template: {str(e)}', 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
