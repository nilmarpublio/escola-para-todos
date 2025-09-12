from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Teste Simples</title>
    </head>
    <body>
        <h1>Teste Simples - Funcionando!</h1>
        <p>Se você vê esta mensagem, o Flask está funcionando normalmente.</p>
        <p>O problema estava no arquivo principal.</p>
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
