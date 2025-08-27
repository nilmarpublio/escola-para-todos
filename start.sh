#!/bin/bash
echo "🚀 Iniciando Escola para Todos com PostgreSQL..."
echo "📁 Diretório atual: $(pwd)"
echo "📋 Arquivos disponíveis:"
ls -la

echo "🗄️ Inicializando banco PostgreSQL..."
echo "📝 Verificando se app_postgres.py existe..."
if [ -f "app_postgres.py" ]; then
    echo "✅ app_postgres.py encontrado!"
    
    echo "🔧 Inicializando banco de dados..."
    python init_db_postgres.py
    
    echo "🐍 Executando gunicorn com app_postgres:app..."
    exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app_postgres:app
else
    echo "❌ app_postgres.py não encontrado!"
    echo "📋 Arquivos Python disponíveis:"
    ls -la *.py
    exit 1
fi
