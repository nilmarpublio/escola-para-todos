import os
from datetime import timedelta

class FlyConfig:
    """Configurações específicas para o Fly.io"""
    
    # Configurações básicas
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fly-secret-key-change-in-production'
    DEBUG = False  # Sempre False em produção
    
    # Configurações de banco de dados PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True  # True em produção com HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configurações de segurança
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Configurações de upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    
    # Configurações de paginação
    POSTS_PER_PAGE = 10
    
    # Configurações específicas do Fly.io
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 8080))
    
    # Configurações de banco de dados
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return 'postgresql://localhost/escola_para_todos'
    
    # Configurações de logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'app.log'
