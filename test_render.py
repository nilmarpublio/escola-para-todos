from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Render! Flask is working! 🚀'

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
