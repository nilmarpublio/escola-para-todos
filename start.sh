#!/bin/bash
echo "🚀 Iniciando Escola para Todos..."
echo "📁 Diretório atual: $(pwd)"
echo "📋 Arquivos disponíveis:"
ls -la

echo "🐍 Executando gunicorn com app_clean:app..."
echo "📝 Verificando se app_clean.py existe..."
if [ -f "app_clean.py" ]; then
    echo "✅ app_clean.py encontrado!"
    exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app_clean:app
else
    echo "❌ app_clean.py não encontrado!"
    echo "📋 Arquivos Python disponíveis:"
    ls -la *.py
    exit 1
fi
