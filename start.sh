#!/bin/bash
echo "🚀 Iniciando Escola para Todos..."
echo "📁 Diretório atual: $(pwd)"
echo "📋 Arquivos disponíveis:"
ls -la

echo "🐍 Executando gunicorn com app_clean:app..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app_clean:app
