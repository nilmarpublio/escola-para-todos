#!/bin/bash
set -e  # Parar se houver erro

echo "🚀 =========================================="
echo "🚀 INICIANDO Aqui se Aprende NO RENDER"
echo "🚀 =========================================="
echo "📁 Diretório atual: $(pwd)"
echo "📋 Arquivos disponíveis:"
ls -la

echo ""
echo "🗄️ =========================================="
echo "🗄️ INICIALIZANDO BANCO POSTGRESQL"
echo "🗄️ =========================================="

# Verificar se DATABASE_URL está configurada
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERRO: DATABASE_URL não está configurada!"
    echo "📋 Variáveis de ambiente disponíveis:"
    env | grep -E "(DATABASE|FLASK|SECRET)" || echo "Nenhuma variável relevante encontrada"
    exit 1
else
    echo "✅ DATABASE_URL configurada: ${DATABASE_URL:0:20}..."
fi

# Verificar se init_db_postgres.py existe
if [ ! -f "init_db_postgres.py" ]; then
    echo "❌ ERRO: init_db_postgres.py não encontrado!"
    echo "📋 Arquivos Python disponíveis:"
    ls -la *.py
    exit 1
fi

echo "🐍 Executando init_db_postgres.py..."
python init_db_postgres.py

echo ""
echo "🌐 =========================================="
echo "🌐 INICIANDO APLICAÇÃO FLASK"
echo "🌐 =========================================="

# Verificar se app_postgres.py existe
if [ ! -f "app_postgres.py" ]; then
    echo "❌ ERRO: app_postgres.py não encontrado!"
    echo "📋 Arquivos Python disponíveis:"
    ls -la *.py
    exit 1
fi

echo "✅ app_postgres.py encontrado!"
echo "🚀 Iniciando gunicorn com app_postgres:app..."
echo "📊 Porta: $PORT"
echo "🌍 Workers: 1"
echo "⏱️ Timeout: 120s"

exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app_postgres:app
