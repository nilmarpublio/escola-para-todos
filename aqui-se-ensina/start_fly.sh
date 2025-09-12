#!/bin/bash
# Script de inicialização para Fly.io

echo "🚀 Iniciando Aqui se Aprende no Fly.io..."

# Verificar se estamos no Fly.io
if [ -n "$FLY_APP_NAME" ]; then
    echo "✅ Detectado ambiente Fly.io: $FLY_APP_NAME"
    
    # Inicializar banco de dados
    echo "🗄️ Inicializando banco de dados..."
    python init_db_postgres.py
    
    # Iniciar aplicação
    echo "🌐 Iniciando aplicação..."
    gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 120 app_postgres:app
else
    echo "❌ Não estamos no Fly.io, usando configuração local"
    python app_postgres.py
fi
