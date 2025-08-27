#!/bin/bash
echo "🚀 Iniciando Escola para Todos..."
echo "📁 Diretório atual: $(pwd)"
echo "📋 Arquivos disponíveis:"
ls -la

echo "🐍 Executando gunicorn com app_minimal:app..."
echo "📝 Verificando se app_minimal.py existe..."
if [ -f "app_minimal.py" ]; then
    echo "✅ app_minimal.py encontrado!"
    exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app_minimal:app
else
    echo "❌ app_minimal.py não encontrado!"
    echo "📋 Arquivos Python disponíveis:"
    ls -la *.py
    exit 1
fi
