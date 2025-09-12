from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user, login_required

def admin_required(f):
    """Decorator que requer que o usuário seja administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash('❌ Acesso negado. Você precisa ser administrador para acessar esta página.', 'error')
            return redirect(url_for('splash'))
        return f(*args, **kwargs)
    return decorated_function

def professor_required(f):
    """Decorator que requer que o usuário seja professor ou administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not (current_user.is_professor or current_user.is_admin):
            flash('❌ Acesso negado. Você precisa ser professor para acessar esta página.', 'error')
            return redirect(url_for('splash'))
        return f(*args, **kwargs)
    return decorated_function

def aluno_required(f):
    """Decorator que requer que o usuário seja aluno"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_aluno:
            flash('❌ Acesso negado. Esta página é destinada apenas para alunos.', 'error')
            return redirect(url_for('splash'))
        return f(*args, **kwargs)
    return decorated_function

def content_creator_required(f):
    """Decorator que requer que o usuário possa criar conteúdo (professor ou admin)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.can_create_content():
            flash('❌ Acesso negado. Você não tem permissão para criar conteúdo.', 'error')
            return redirect(url_for('splash'))
        return f(*args, **kwargs)
    return decorated_function

def user_management_required(f):
    """Decorator que requer que o usuário possa gerenciar usuários (apenas admin)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.can_manage_users():
            flash('❌ Acesso negado. Você não tem permissão para gerenciar usuários.', 'error')
            return redirect(url_for('splash'))
        return f(*args, **kwargs)
    return decorated_function

def analytics_required(f):
    """Decorator que requer que o usuário possa visualizar analytics (professor ou admin)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.can_view_analytics():
            flash('❌ Acesso negado. Você não tem permissão para visualizar analytics.', 'error')
            return redirect(url_for('splash'))
        return f(*args, **kwargs)
    return decorated_function

def owner_or_admin_required(resource_owner_id):
    """Decorator que requer que o usuário seja o dono do recurso ou administrador"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            # Admin pode acessar qualquer recurso
            if current_user.is_admin:
                return f(*args, **kwargs)
            
            # Verifica se o usuário é o dono do recurso
            if current_user.id != resource_owner_id:
                flash('❌ Acesso negado. Você só pode gerenciar seus próprios recursos.', 'error')
                return redirect(url_for('splash'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(permission):
    """Decorator genérico que requer uma permissão específica"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            if permission not in current_user.get_required_permissions():
                flash(f'❌ Acesso negado. Você não tem a permissão "{permission}".', 'error')
                return redirect(url_for('splash'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def active_user_required(f):
    """Decorator que requer que o usuário esteja ativo"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_active:
            flash('❌ Sua conta foi desativada. Entre em contato com o administrador.', 'error')
            return redirect(url_for('logout'))
        return f(*args, **kwargs)
    return decorated_function

def guest_required(f):
    """Decorator que requer que o usuário NÃO esteja logado (para páginas de login/registro)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash('ℹ️ Você já está logado.', 'info')
            return redirect(url_for('splash'))
        return f(*args, **kwargs)
    return decorated_function

# Função auxiliar para verificar permissões em templates
def has_permission(permission):
    """Verifica se o usuário atual tem uma permissão específica"""
    if not current_user.is_authenticated:
        return False
    return permission in current_user.get_required_permissions()

# Função auxiliar para verificar tipo de usuário em templates
def is_user_type(user_type):
    """Verifica se o usuário atual é de um tipo específico"""
    if not current_user.is_authenticated:
        return False
    
    if user_type == 'admin':
        return current_user.is_admin
    elif user_type == 'professor':
        return current_user.is_professor
    elif user_type == 'aluno':
        return current_user.is_aluno
    
    return False
