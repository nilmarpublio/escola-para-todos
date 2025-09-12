# Configurações para desenvolvimento local
import os

# Configurações da Aplicação
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'
os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Configurações do Banco PostgreSQL Local
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_NAME'] = 'escola_para_todos'
os.environ['DB_USER'] = 'escola_user'
os.environ['DB_PASSWORD'] = 'escola123'
os.environ['DB_PORT'] = '5432'
